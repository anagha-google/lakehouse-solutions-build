# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# ======================================================================================
# ABOUT
# In this PySpark script, perform analytics on the augmented telco customer churn data
# to arrive at KPI metrics and persist to GCS and create an external table in BigQuery
# on the data in GCS
# ======================================================================================

import configparser
from datetime import datetime
import os
import json
from pyspark.sql import SparkSession
from pyspark.sql.functions import udf, col, substring, lit, when, avg
from pyspark.sql import functions as F
from pyspark.sql.functions import input_file_name
import random
from pyspark.sql.types import *
from pyspark.sql.functions import year, month, dayofmonth, hour, weekofyear, dayofweek, date_format
from pyspark import SparkContext, SparkConf, SQLContext
from google.cloud import storage
from google.cloud import bigquery
import sys


# Parse arguments
projectID=sys.argv[1]
bqDatasetName=sys.argv[2]
sourceBucketName=sys.argv[3]

# Source data definition
curatedTelcoPerformanceDataDir="gs://"+sourceBucketName+"/output_data/telco_performance_augmented/part*"

# Output directory declaration
outputGCSURI="gs://"+sourceBucketName+"/output_data/kpis_by_customer"


# Get or create a Spark session
spark =SparkSession.builder.appName("KPIs-By-Customer").config('spark.jars', 'gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar').getOrCreate()

# Read the source data into a dataframe
curatedTelcoPerformanceDataDF = spark.read.format("parquet").option("header", True).option("inferSchema",True).load(curatedTelcoPerformanceDataDir)
curatedTelcoPerformanceDataDF.printSchema()
#curatedTelcoPerformanceDataDF.show(3,truncate=False)

# Layer 1 slicing - Avg of performance metrics at customer granularity level
curatedTelcoPerformanceDataDF=curatedTelcoPerformanceDataDF.drop(curatedTelcoPerformanceDataDF.months)
# Create a temp view
curatedTelcoPerformanceDataDF.createOrReplaceTempView("telco_perf_by_customer_unaggregated")
# Derive month natively without SQL Context
from pyspark.sql.window import Window
curatedTelcoPerformanceDataAugDF1 = curatedTelcoPerformanceDataDF.withColumn(
    "month", 
    F.row_number().over(Window.partitionBy("customer_ID").orderBy("customer_ID"))
)
# Define the base metrics to average
cols_to_avg = [
    "PRBUsageUL", "PRBUsageDL", "meanThr_DL", "meanThr_UL", "maxThr_DL", "maxThr_UL",
    "meanUE_DL", "meanUE_UL", "maxUE_DL", "maxUE_UL", "maxUE_UL_DL", "Unusual",
    "roam_Mean", "change_mou", "drop_vce_Mean", "drop_dat_Mean", "blck_vce_Mean",
    "blck_dat_Mean", "plcd_vce_Mean", "plcd_dat_Mean", "comp_vce_Mean", "comp_dat_Mean",
    "peak_vce_Mean", "peak_dat_Mean", "mou_peav_Mean", "mou_pead_Mean", "opk_vce_Mean",
    "opk_dat_Mean", "mou_opkv_Mean", "mou_opkd_Mean", "drop_blk_Mean", "callfwdv_Mean",
    "callwait_Mean"
]

# Calculate averages of metrics by customer_ID,CellName,tenure,PhoneService,MultipleLines,InternetService
# for customers signed up for phone service
agg_exprs = [F.avg(c).alias(f"avg_{c}") for c in cols_to_avg]

curatedTelcoPerformanceAggrDF = curatedTelcoPerformanceDataAugDF1 \
    .filter(col("PhoneService") == 'Yes') \
    .groupBy("customer_ID", "CellName", "tenure", "PhoneService", "MultipleLines", "InternetService") \
    .agg(*agg_exprs)

# Augment with customer grain performance metrics
DF1 = curatedTelcoPerformanceAggrDF.select(
    "*",
    (col("avg_plcd_vce_Mean") - col("avg_comp_vce_Mean")).alias("incomplete_voice_calls"),
    (col("avg_plcd_dat_Mean") - col("avg_comp_dat_Mean")).alias("incomplete_data_calls"),
    (col("avg_peak_vce_Mean") / col("avg_opk_vce_Mean")).alias("service_stability_voice_calls"),
    (col("avg_peak_dat_Mean") / col("avg_opk_dat_Mean")).alias("service_stability_data_calls")
)

# Replace nulls with 0 across columns
DF2 = DF1.fillna(value=0)

# Compute global averages ONE TIME instead of triggering dozens of `collect()` jobs
metrics_to_avg = [
    "avg_PRBUsageUL", "avg_PRBUsageDL", "avg_maxThr_DL", "avg_maxThr_UL", 
    "avg_meanUE_DL", "avg_meanUE_UL", "avg_maxUE_DL", "avg_maxUE_UL", 
    "avg_maxUE_UL_DL", "avg_drop_vce_Mean", "avg_drop_dat_Mean", 
    "avg_blck_vce_Mean", "avg_blck_dat_Mean", "avg_meanThr_DL", "avg_meanThr_UL", 
    "avg_roam_Mean", "avg_change_mou", "avg_peak_vce_Mean", "avg_peak_dat_Mean", 
    "avg_opk_vce_Mean", "avg_opk_dat_Mean", "avg_drop_blk_Mean", "avg_callfwdv_Mean", 
    "service_stability_voice_calls", "service_stability_data_calls"
]

try:
    global_avgs_row = DF2.select([avg(c).alias(c) for c in metrics_to_avg]).collect()[0].asDict()
except (IndexError, AttributeError) as e:
    print(f"WARNING: No data found for metrics in DF2. Defaulting to 0 for threshold comparisons. Details: {e}")
    global_avgs_row = {c: 0 for c in metrics_to_avg}

greater_is_one = [
    "avg_PRBUsageUL", "avg_PRBUsageDL", "avg_maxThr_DL", "avg_maxThr_UL", 
    "avg_meanUE_DL", "avg_meanUE_UL", "avg_maxUE_DL", "avg_maxUE_UL", 
    "avg_maxUE_UL_DL", "avg_drop_vce_Mean", "avg_drop_dat_Mean", 
    "avg_blck_vce_Mean", "avg_blck_dat_Mean"
]
less_is_one = [
    "avg_meanThr_DL", "avg_meanThr_UL", "avg_roam_Mean", "avg_change_mou", 
    "avg_peak_vce_Mean", "avg_peak_dat_Mean", "avg_opk_vce_Mean", "avg_opk_dat_Mean", 
    "avg_drop_blk_Mean", "avg_callfwdv_Mean", "service_stability_voice_calls", 
    "service_stability_data_calls"
]

threshold_cols = []
for c in greater_is_one:
    out_col = "change_mouL_Thrsld" if c == "avg_change_mou" else c + "_Thrsld"
    threshold_cols.append(when(col(c) > lit(global_avgs_row[c]), 1).otherwise(0).alias(out_col))

for c in less_is_one:
    out_col = "change_mouL_Thrsld" if c == "avg_change_mou" else c + "_Thrsld"
    threshold_cols.append(when(col(c) < lit(global_avgs_row[c]), 1).otherwise(0).alias(out_col))

# Add derived columns that are customer grain performance metrics of 0's and 1s
DF3 = DF2.select("*", *threshold_cols)

# Replace nulls with 0 across columns
DF3 = DF3.fillna(value=0)

# Add a defect count column which sums up the various metrics that are either 0 or 1
thrsld_column_names = [c + "_Thrsld" if c != "avg_change_mou" else "change_mouL_Thrsld" for c in greater_is_one + less_is_one]
defect_expr = col(thrsld_column_names[0])
for c in thrsld_column_names[1:]:
    defect_expr = defect_expr + col(c)

finalDF = DF3.withColumn("defect_count", defect_expr)
finalDF.show(3,truncate = False)

# Record count
finalDF.count()

# Persist to GCS
finalDF.write.parquet(outputGCSURI, mode = "overwrite")

# Construct a BigQuery external table definition on the data persisted to GCS
query = f"""
CREATE OR REPLACE EXTERNAL TABLE """+bqDatasetName+""".kpis_by_customer OPTIONS (
format = 'PARQUET', uris = ['"""+outputGCSURI+"""/*.parquet'] );
"""

# Execute the BigQuery external table definition
bq_client = bigquery.Client(project=projectID)
job = bq_client.query(query)
job.result()



