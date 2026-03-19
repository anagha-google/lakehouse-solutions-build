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
# In this PySpark script, perform analytics on the augmented telco customer churn data-
# 1. Calculate KPI metrics by customer, by cell tower & flag towers needing maintenance
# 2. and persist to GCS 
# 3. and create an external table in BigQuery on the KPIs in GCS
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
augmentedTelcoPerformanceDataDir="gs://"+sourceBucketName+"/output_data/telco_performance_augmented/*"

# Output directory declaration
outputGCSURI="gs://"+sourceBucketName+"/output_data/kpis_by_cell_tower"

# Get or create a Spark session
spark =SparkSession.builder.appName("KPIs-By-Cell-Tower").config('spark.jars', 'gs://spark-lib/bigquery/spark-bigquery-latest_2.12.jar').getOrCreate()

# Read the source data into a dataframe
curatedTelcoPerformanceDataDF = spark.read.format("parquet").option("header", True).option("inferSchema",True).load(augmentedTelcoPerformanceDataDir)
curatedTelcoPerformanceDataDF.printSchema()

# Layer2 slicing: KPIs at cell tower grain level on top of KPIs by customer grain
# ...Drop months
curatedTelcoPerformanceDataDF=curatedTelcoPerformanceDataDF.drop(curatedTelcoPerformanceDataDF.months)
# ...Create a temp view
curatedTelcoPerformanceDataDF.createOrReplaceTempView("telco_perf_by_customer_unaggregated")
# ...Derive month
curatedTelcoPerformanceDataAugDF1 = spark.sql('''select *,  ROW_NUMBER()  OVER(PARTITION BY customerID ORDER BY customerID) AS month from telco_perf_by_customer_unaggregated''')
# ...Create a temp view
curatedTelcoPerformanceDataAugDF1.createOrReplaceTempView("telco_perf_by_customer_unaggregated_with_month")

# Calculate averages of metrics by customerID,CellName,tenure,PhoneService,MultipleLines,InternetService
# for customers signed up for phone service
curatedTelcoPerformanceAggrDF = spark.sql('''select customerID,CellName,tenure,PhoneService,MultipleLines,InternetService,avg(PRBUsageUL) as avg_PRBUsageUL,avg(PRBUsageDL) as avg_PRBUsageDL,avg(meanThr_DL) as avg_meanThr_DL,avg(meanThr_UL) as avg_meanThr_UL,avg(maxThr_DL) as avg_maxThr_DL,avg(maxThr_UL) as avg_maxThr_UL,avg(meanUE_DL) as avg_meanUE_DL,avg(meanUE_UL) as avg_meanUE_UL,avg(maxUE_DL) as avg_maxUE_DL,avg(maxUE_UL) as avg_maxUE_UL,avg(maxUE_UL_DL) as avg_maxUE_UL_DL,avg(Unusual) as avg_Unusual,avg(roam_Mean) as avg_roam_Mean,avg(change_mou) as avg_change_mou,avg(drop_vce_Mean) as avg_drop_vce_Mean,avg(drop_dat_Mean) as avg_drop_dat_Mean,avg(blck_vce_Mean) as avg_blck_vce_Mean,avg(blck_dat_Mean) as avg_blck_dat_Mean,avg(plcd_vce_Mean) as avg_plcd_vce_Mean,avg(plcd_dat_Mean) as avg_plcd_dat_Mean,avg(comp_vce_Mean) as avg_comp_vce_Mean,avg(comp_dat_Mean) as avg_comp_dat_Mean,avg(peak_vce_Mean) as avg_peak_vce_Mean,avg(peak_dat_Mean) as avg_peak_dat_Mean,avg(mou_peav_Mean) as avg_mou_peav_Mean,avg(mou_pead_Mean) as avg_mou_pead_Mean,avg(opk_vce_Mean) as avg_opk_vce_Mean,avg(opk_dat_Mean) as avg_opk_dat_Mean,avg(mou_opkv_Mean) as avg_mou_opkv_Mean,avg(mou_opkd_Mean) as avg_mou_opkd_Mean,avg(drop_blk_Mean) as avg_drop_blk_Mean,avg(callfwdv_Mean) as avg_callfwdv_Mean,avg(callwait_Mean) as avg_callwait_Mean  from telco_perf_by_customer_unaggregated_with_month where PhoneService = 'Yes'  group by customerID,CellName,tenure,PhoneService,MultipleLines,InternetService  ''')
# ...Create a temp view
curatedTelcoPerformanceAggrDF.createOrReplaceTempView("telco_perf_by_customer_aggregated")

# Calculate averages of metrics by cell tower name
aggregatedTelcoPerformanceByCellTowerDF = spark.sql('''select CellName,count(customerID) as customerID_count,avg(avg_PRBUsageUL) as avg_PRBUsageUL,avg(avg_PRBUsageDL) as avg_PRBUsageDL,avg(avg_meanThr_DL) as avg_meanThr_DL,avg(avg_meanThr_UL) as avg_meanThr_UL,avg(avg_maxThr_DL) as avg_maxThr_DL,avg(avg_maxThr_UL) as avg_maxThr_UL,avg(avg_meanUE_DL) as avg_meanUE_DL,avg(avg_meanUE_UL) as avg_meanUE_UL,avg(avg_maxUE_DL) as avg_maxUE_DL,avg(avg_maxUE_UL) as avg_maxUE_UL,avg(avg_maxUE_UL_DL) as avg_maxUE_UL_DL,avg(avg_Unusual) as avg_Unusual,avg(avg_roam_Mean) as avg_roam_Mean,avg(avg_change_mou) as avg_change_mou,avg(avg_drop_vce_Mean) as avg_drop_vce_Mean,avg(avg_drop_dat_Mean) as avg_drop_dat_Mean,avg(avg_blck_vce_Mean) as avg_blck_vce_Mean,avg(avg_blck_dat_Mean) as avg_blck_dat_Mean,avg(avg_plcd_vce_Mean) as avg_plcd_vce_Mean,avg(avg_plcd_dat_Mean) as avg_plcd_dat_Mean,avg(avg_comp_vce_Mean) as avg_comp_vce_Mean,avg(avg_comp_dat_Mean) as avg_comp_dat_Mean,avg(avg_peak_vce_Mean) as avg_peak_vce_Mean,avg(avg_peak_dat_Mean) as avg_peak_dat_Mean,avg(avg_mou_peav_Mean) as avg_mou_peav_Mean,avg(avg_mou_pead_Mean) as avg_mou_pead_Mean,avg(avg_opk_vce_Mean) as avg_opk_vce_Mean,avg(avg_opk_dat_Mean) as avg_opk_dat_Mean,avg(avg_mou_opkv_Mean) as avg_mou_opkv_Mean,avg(avg_mou_opkd_Mean) as avg_mou_opkd_Mean,avg(avg_drop_blk_Mean) as avg_drop_blk_Mean,avg(avg_callfwdv_Mean) as avg_callfwdv_Mean,avg(avg_callwait_Mean) as avg_callwait_Mean  from telco_perf_by_customer_aggregated group by CellName''')

# Augment with cell tower grain performance metrics
slice2DF1=aggregatedTelcoPerformanceByCellTowerDF.withColumn('service_stability_voice_calls',aggregatedTelcoPerformanceByCellTowerDF.avg_peak_vce_Mean/aggregatedTelcoPerformanceByCellTowerDF.avg_opk_vce_Mean   )
slice2DF2=slice2DF1.withColumn('service_stability_data_calls',slice2DF1.avg_peak_dat_Mean/slice2DF1.avg_opk_dat_Mean )
slice2DF3=slice2DF2.withColumn('Incomplete_voice_calls',slice2DF2.avg_plcd_vce_Mean -slice2DF2.avg_comp_vce_Mean )
slice2DF4=slice2DF3.withColumn('Incomplete_data_calls',slice2DF3.avg_plcd_dat_Mean -slice2DF3.avg_comp_dat_Mean )

# Calculate global averages ONE TIME to avoid redundant Spark jobs
metrics_to_avg = [
    "avg_PRBUsageUL", "avg_PRBUsageDL", "avg_meanThr_DL", "avg_meanThr_UL", 
    "avg_maxThr_DL", "avg_maxThr_UL", "avg_meanUE_DL", "avg_meanUE_UL", 
    "avg_maxUE_DL", "avg_maxUE_UL", "avg_maxUE_UL_DL", 
    "avg_roam_Mean", "avg_change_mou", "avg_drop_vce_Mean", "avg_drop_dat_Mean", 
    "avg_blck_vce_Mean", "avg_blck_dat_Mean", "avg_peak_vce_Mean", "avg_peak_dat_Mean", 
    "avg_opk_vce_Mean", "avg_opk_dat_Mean", "avg_drop_blk_Mean", "avg_callfwdv_Mean", 
    "service_stability_voice_calls", "service_stability_data_calls"
]

global_avgs_row = slice2DF4.select([F.avg(c).alias(c) for c in metrics_to_avg]).collect()[0].asDict()

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
    threshold_cols.append(F.when(F.col(c) > F.lit(global_avgs_row[c]), 1).otherwise(0).alias(c + "_Thrsld"))

for c in less_is_one:
    out_col = "change_mouL_Thrsld" if c == "avg_change_mou" else c + "_Thrsld"
    threshold_cols.append(F.when(F.col(c) < F.lit(global_avgs_row[c]), 1).otherwise(0).alias(out_col))

# Add all threshold columns in one select and replace nulls with 0
slice2DF30 = slice2DF4.select("*", *threshold_cols).fillna(value=0)
slice2DF30.show(3, truncate=False)

# ...Calculate defect count
thrsld_columns = [F.col(c + "_Thrsld" if c != "avg_change_mou" else "change_mouL_Thrsld") for c in greater_is_one + less_is_one]
defect_expr = thrsld_columns[0]
for col_expr in thrsld_columns[1:]:
    defect_expr = defect_expr + col_expr

slice2DF31 = slice2DF30.withColumn("defect_count", defect_expr)

# ...Calculate if maintenance is required (defect >= 15)
finalDF= slice2DF31.withColumn("Maintainence_Required",when(col("defect_count")>=15,"Required").otherwise("Not Required"))

# ...Record count
finalDF.count()

# Persist to GCS
finalDF.write.parquet(outputGCSURI, mode = "overwrite")

# Construct a BigQuery external table definition on the data persisted to GCS
query = f"""
CREATE OR REPLACE EXTERNAL TABLE """+bqDatasetName+""".kpis_by_cell_tower OPTIONS (
format = 'PARQUET', uris = ['"""+outputGCSURI+"""/*.parquet'] );
"""

# Execute the BigQuery external table definition
bq_client = bigquery.Client(project=projectID)
job = bq_client.query(query)
job.result()

# Print the cell tower name, defect count and maintenance required flag 
finalSubsetDF=finalDF.select(col("CellName"),col("defect_count"),col("Maintainence_Required"))
finalSubsetDF.show(3,truncate= False)