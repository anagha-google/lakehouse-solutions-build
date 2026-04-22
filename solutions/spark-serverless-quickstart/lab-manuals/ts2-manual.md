*Copyright 2026 Google LLC*

*Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at*

*http://www.apache.org/licenses/LICENSE-2.0*

*Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.*


<hr>

# Technical Solution 2: Interactive notebooks with serverless Managed Service for Apache Spark on Google Cloud

## 1.0. About the lab

### 1.1. Abstract
This lab is **introductory** in nature and showcases **serverless Managed Service for Apache Spark - Interactive Sessions** feature.  The goal of the lab is to demystify this feature through a (zero fluff, zero dazzle) minimum viable end to end sample to accelerate adoption. This hands-on lab complements the blog post [Lakehouse Demystified - Part 3: Managed service for Apache Spark - serverless interactive sessions for Spark notebooks]() and uses the same infrastructure as technical solution 1.


|  |  | 
| -- | :--- | 
| Technical Focus| **Spark notebooks powered by serverless Managed Service for Apache Spark on Google Cloud** |
| Use case |  Chicago Crimes Analysis |
| Notebook platforms |  Colab notebooks in BigQuery Studio<br>Notebooks on Vertex AI Workbench<br>Notebooks on BYO Jupyter<br>Notebooks in VS Code |

#### What to expect:

See the "Lab Flow" section below.

<hr>

### 1.2. Lab format

- Is fully scripted - the entire solution is provided, and with instructions
- Is self-paced/self-service

<hr>


### 1.3. Duration
The hands-on lab takes ~0.5 hours or less to complete

<hr>

### 1.4. Prerequisites

- Completion of Technical Solution 1.
- VS Code insatlled on your machine if you want to try out Spark notebooks powered by serverless interactive sessions

<hr>

### 1.5. Resources provisioned
We will reuse the resources provisioned in technical solution 1, and only create something called 'Interactive Sessions Template'.

<hr>

### 1.6. Audience

- A quick read for architects
- Targeted for hands on practitioners, especially data engineers, data analysts and data scientists

<hr>

### 1.7. Features & Functionality covered

|| Features & Functionality | 
| -- | :--- | 
| 1|Interactive sessions creation from command line and walk through of the UI |
| 2|Interactive sessions template creation from command line and walk through of the UI |
| 3|Colab Spark notebook execution powered by serverless interactive spark sessions, based off of configs in the Spark Connect sessions template  |
| 4|Vertex AI Workbench creation and Spark notebook execution powered by serverless interactive spark sessions, based off of configs in the Jupyter sessions template  |
| 5|Local Jupyter server installation and Spark notebook execution powered by serverless interactive spark sessions, based off of configs in the Jupyter sessions template  |
| 6|Data Agent Kit plugin installation in VS Code and Spark notebook execution powered by serverless interactive spark sessions, based off of configs in the Jupyter sessions template  |

Note: The catalog component, Lakehouse runtime catalog is covered in the next technical solution.

<hr>

### 1.8. Architecture

#### 1.8.1. Managed Service for Apache Spark - Integration Landscape

Please refer to the blog post [Lakehouse Demystified - Part 2: Managed service for Apache Spark - serverless batches]() for an explanation of this diagram.

![README](../images/ts2-02.png)   
<br><br>


#### 1.8.2. Reference Architecture

Please refer to the [Lakehouse Demystified - Part 3: Managed service for Apache Spark - serverless interactive sessions for Spark notebooks]() blog post for a narrative.

![README](../images/ts2-03.png)   
<br><br>

A more simplistic version...

![README](../images/ts2-01.png)   
<br><br>

<hr>

#### 1.8.3. Lab Solution Architecture

In the lab, we will simulate a data analyst that read data, transforms it a bit for analysis and visualizes it. We will read Chicago crimes public dataset in BigQuery with the Spark BigQuery connector from Google Cloud, from the different notebook flavors. We will analyze crimes and visualize them in the notebooks. Note that the lab is less about Apache Spark and more about the serverless Spark sessions support in notebooks, so the labs are basic.

![README](../images/ts2-05.png)   
<br><br>

<hr>


### 1.9. Lab Flow

![README](../images/ts2-04.png)   
<br><br>

<hr>

### 1.10. For success

Read the blog posts and the lab narrative below, review the code, and then start trying out the lab.

<hr>



# 2. Product Highlights

Read the blog post [Lakehouse Demystified - Part 2: Managed service for Apache Spark - serverless batches]() for a comprehensive of managed serverless Spark on Google Cloud. Please refer to the [Lakehouse Demystified - Part 3: Managed service for Apache Spark - serverless interactive sessions for Spark notebooks]() blog post for comprehensive coverage on interactive sessions.

## 2.1.  Interactive sessions
Interactive sessions on serverless Managed Service for Apache Spark are essentially dedicated serverless Spark infrastructure that can be attached to notebooks for interactive authoring of Spark code. There are two options to connect notebooks to interactive sessions - Spark Connect and Jupyter. BigQuery studio offers Colab notebooks that work with Spark Connect, any Jupyter compatible notebook platform works well with remote Jupyter kernels. Google Cloud's Data Cloud Extension for IDEs allow you to author notebooks in your IDEs with remote Jupyter kernels. 

## 2.2. Language support
Google Cloud is strategically investing in supporting PySpark. 

## 2.3. Interactive session templates
Interactive session templates are a construct that can be used to define the core and common serverless infrastructure specifications & guardrails - such as runtime versions, baseline resources for driver & executor, min-max thresholds for executors, custom containers, packages, metastore/catalog configurations and more. These promote consistency and reduce toil of defining the configs over and over again in each notebook. These templates can be imported into the Spark session creation command to take advantage of the predefined configurations. This is demonstrated in the lab. [Read the product documenation](https://docs.cloud.google.com/dataproc-serverless/docs/guides/create-serverless-sessions-templates)

## 2.4. Identity supported
Interactive sessions support both User Managed Service Accounts (UMSAs - non human application IDs) as well as end user credentials (EUC). You can configure this at the session template level.

<hr>

# 3. Lab

<hr>

## 3.1. Setup -  initialize active gcloud configuration

Run the following commands in Cloud Shell to authenticate and configure your active project:

1. Initialization:
```
gcloud init
```

2. Set the active Google Cloud project target:
```
gcloud config set project <YOUR_GCP_PROJECT_ID>
```

3. Set the quota project for ADC (Application Default Credentials):
```
gcloud auth application-default set-quota-project <YOUR_GCP_PROJECT_ID>
```

<hr>


## 3.2. Setup - create an interactive sessions template for Spark Connect, for PySpark and using a Service Account 

To recap - session template is to bootstrap of common configurations to standardize, reduce toil, and spped development/analysis cycles. 
1. There is no gcloud command to create session templates, so we will use the Console.
2. We will use a service account for the session template instead of individual user for simplicity. Our service account already has all permissions. This means that Spark will run and access data as the configured service account.

### 3.2.1. Capture the service account fully qualified name (FQN)

Navigate to Cloud IAM and find the service account as show below and copy it.

![README](../images/ts2-06.png)   
<br><br>

<hr>

### 3.2.2. Navigate to the Managed Service for Apache Spark 'session templates' UI

Follow the screenshots below to navigate to the Managed Service for Apache Spark 'session templates' UI

![README](../images/ts2-07a.png)   
<br><br>

![README](../images/ts2-07b.png)   
<br><br>

<hr>

### 3.2.3. Create the session template

Follow the screenshots below to create a session template. Ensure you make the same selections.

![README](../images/ts2-08a.png)   
<br><br>

<hr>

![README](../images/ts2-08b.png)   
<br><br>

<hr>

![README](../images/ts2-08c.png)   
<br><br>

<hr>

![README](../images/ts2-08d.png)   
<br><br>

![README](../images/ts2-08e.png)   
<br><br>

<hr>

![README](../images/ts2-08f.png)   
<br><br>

<hr>

![README](../images/ts2-08g.png)   
<br><br>

<hr>

## 3.3. Setup - create an interactive sessions template for Jupyter, for PySpark and using a Service Account 


Follow the screenshots below to create a session template. Ensure you make the same selections.

![README](../images/ts2-09a.png)   
<br><br>

<hr>

![README](../images/ts2-09b.png)   
<br><br>

<hr>

![README](../images/ts2-09c.png)   
<br><br>

<hr>

![README](../images/ts2-09d.png)   
<br><br>

![README](../images/ts2-09e.png)   
<br><br>

<hr>

![README](../images/ts2-09f.png)   
<br><br>

<hr>


## 3.4. Setup - Provision Gemini Enterprise Workbench instance

Gemini Enterprise Workbench instance (formerly called Vertex AI Workbench instance) is an optional notebook server that can be created for Data Scientists and ML engineers to experiment. Spark notebooks powered by Managed Service for Apache Spark interactive sessions are supported. Lets create the workbench instance.

Follow the screenshots below to stand up Gemini Enterprise Workbench instance and start up a notebook with a session.

![README](../images/ts2-10a.png)   
<br><br>

![README](../images/ts2-10b.png)   
<br><br>

![README](../images/ts2-10c.png)   
<br><br>

![README](../images/ts2-10d.png)   
<br><br>

![README](../images/ts2-10e.png)   
<br><br>

![README](../images/ts2-10f.png)   
<br><br>

<hr>

Lets try a notebook.

![README](../images/ts2-10g.png)   
<br><br>

![README](../images/ts2-10h.png)   
<br><br>

![README](../images/ts2-10i.png)   
<br><br>

![README](../images/ts2-10j.png)   
<br><br>

![README](../images/ts2-10k.png)   
<br><br>

![README](../images/ts2-10l.png)   
<br><br>


<hr>

## 3.5. Setup - Install local Jupyter on your machine

This is the documentation page. https://docs.cloud.google.com/dataproc-serverless/docs/quickstarts/jupyterlab-sessions#install-jupyterlab-extension
The author used a slightly different approach as detailed below.

### 3.5.1. Authenticate to gcloud

1. Run the command below - it will use the credentials obtained from the login flow to also update the Application Default Credentials, making them available to client libraries
```
gcloud auth login --update-adc
```

2. Create a virtual environment
```
python -m venv .venv
source .venv/bin/activate
```

3. Install jupyterlab and more
```
pip install --upgrade pip
pip install jupyterlab
pip install bigquery-jupyter-plugin
pip install pyOpenSSL
```

4. Launch JupyterLab
```
jupyter lab
```

![README](../images/ts2-11a.png)   
<br><br>



5. This will open a browser window with a launcher as shown below. Click on the session template.
![README](../images/ts2-11b.png)   
<br><br>

6. Quick test

![README](../images/ts2-11c.png)   
<br><br>

<hr>




## 3.6. Execute a Spark notebook in Colab in BigQuery studio with Spark Connect


<hr>

## 3.7. Execute a Spark notebook on Vertex AI Workbench with Jupyter


<hr>

## 3.8. Execute a Spark notebook in VS Code on your machine


<hr>

## 3.9. Execute a Spark notebook on local Jupyter on your machine


<hr>





##### =====================================================================================================
##### THIS CONCLUDES THE LAB - SPARK NOTEBOOKS POWERED BY MANAGED SPARK SERVERLESS
##### SHUT DOWN THE LAB PROJECT TO AVOID BILLING OR PROCEED TO NEXT TECHNICAL SOLUTION
##### =====================================================================================================


