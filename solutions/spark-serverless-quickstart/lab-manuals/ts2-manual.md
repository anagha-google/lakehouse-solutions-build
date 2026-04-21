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

# Technical Solution 2: Interactive notebooks with Managed Service for Apache Spark on Google Cloud

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
Nothing new.

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
| 6|Data Cloud Extension installation in VS Code and Spark notebook execution powered by serverless interactive spark sessions, based off of configs in the Jupyter sessions template  |

<hr>

### 1.8. Lab Architecture

#### 1.8.1. Managed Service for Apache Spark - Integration Landscape

Please refer to the blog post [Lakehouse Demystified - Part 2: Managed service for Apache Spark - serverless batches]() for an explanation of this diagram.

![README](../images/ts2-02.png)   
<br><br>


#### 1.8.1. Reference Architecture

Please refer to the [Lakehouse Demystified - Part 3: Managed service for Apache Spark - serverless interactive sessions for Spark notebooks]() blog post for a narrative.

![README](../images/ts2-03.png)   
<br><br>

And a little easier on the eyes-

![README](../images/ts2-01.png)   
<br><br>

<hr>

#### 1.8.2. Solution Architecture

![README](../images/TODO.png)   
<br><br>

<hr>


### 1.9. Lab Flow

![README](../images/ts2-04.png)   
<br><br>

<hr>

### 1.10. The data

![README](images/TODO.png)   
<br><br>

<hr>

### 1.11. For success

Read the lab - narrative below, review the code, and then start trying out the lab.

<hr>



# 2. Product Highlights

This hands-on lab complements the blog post [Lakehouse Demystified - Part 3: Managed service for Apache Spark - serverless interactive sessions for Spark notebooks](). Reading the blog is recommended for full understanding of serverless Managed service for Apache Spark product. The following is an overview of the product.

## 2.1. Serverless Managed Service for Apache Spark 

### About
Use Serverless Managed Service for Apache Spark  to run Spark batch workloads without provisioning and managing your own cluster. Specify workload parameters, and then submit the workload to the service. The service will run the workload on a managed compute infrastructure, autoscaling resources as needed. Serverless Managed Service for Apache Spark  charges apply only to the time when the workload is executing.

### Supported workload types
There are two ways to run Serverless Managed Service for Apache Spark workloads: batch workloads and interactive sessions.

#### Batch workloads
Submit a batch workload to the Serverless for Apache Spark service using the Google Cloud console, Google Cloud CLI, or Dataproc API. The service runs the workload on a managed compute infrastructure, autoscaling resources as needed. Serverless for Apache Spark charges apply only to the time when the workload is executing. You can run applications in PySpark, Spark SQL, Spark (Java or Scala). You can specify Spark properties when you submit a serverless Spark batch workload.  

#### Interactive sessions
Write and run code in Jupyter notebooks during a Serverless for Apache Spark interactive session. **This is the feature covered in this hands-on lab.** You can create a notebook session in the following ways:

- Run PySpark code in BigQuery Studio notebooks. Open a BigQuery Python notebook to create a Spark-Connect-based Serverless for Apache Spark interactive session. Each BigQuery notebook can have only one active Serverless for Apache Spark session associated with it.
  
- Use the Managed Service for Apache Spark JupyterLab plugin to create multiple Jupyter notebook sessions from templates that you create and manage. When you install the plugin on a local machine or Compute Engine VM, different cards that correspond to different Spark kernel configurations appear on the JupyterLab launcher page. Click a card to create a Serverless for Apache Spark notebook session, then start writing and testing your code in the notebook. There are other notebook options covered in this lab.

[Learn more](https://docs.cloud.google.com/dataproc-serverless/docs/guides/create-serverless-sessions-templates)

<hr>

# 3. Lab

<hr>

## 3.1. Setup

### 3.1.1. Initialize active gcloud configuration

Run the following commands in Cloud Shell to authenticate and configure your active project:

1. Initialization:
```
gcloud init
```

2. Set the active project target:
```
gcloud config set project <YOUR_PROJECT_ID>
```

3. Set the quota project for ADC (Application Default Credentials):
```
gcloud auth application-default set-quota-project <YOUR_PROJECT_ID>
```

<hr>

### 3.1.2. Provision Vertex AI Workbench instance


<hr>

### 3.1.3. Install local Jupyter on your machine

<hr>

### 3.1.4. Explore the resources specific to this lab 

#TODO


<hr>

## 3.2. Create an 'Interactive Sessions' templates

### 3.2.1. Create a template for Spark Connect



<hr>

### 3.2.1. Create a template for Jupyter



<hr>

## 3.3. Execute a Spark notebook in Colab in BigQuery studio with Spark Connect


<hr>

## 3.4. Execute a Spark notebook on Vertex AI Workbench with Jupyter


<hr>

## 3.5. Execute a Spark notebook in VS Code on your machine


<hr>

## 3.6. Execute a Spark notebook on local Jupyter on your machine


<hr>





##### =====================================================================================================
##### THIS CONCLUDES THE LAB - SPARK NOTEBOOKS POWERED BY MANAGED SPARK SERVERLESS
##### SHUT DOWN THE LAB PROJECT TO AVOID BILLING OR PROCEED TO NEXT TECHNICAL SOLUTION
##### =====================================================================================================


