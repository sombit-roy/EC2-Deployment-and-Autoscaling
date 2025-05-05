# EC2-Deployment-and-Autoscaling

In this project, we will develop an elastic face recognition application using the IaaS resources from AWS. The architecture diagram is shown below -
![](Architecture.png)

The web tier will receive face recognition requests from users via a POST request, store all the input images in an S3 bucket as key-value pairs, forward the recognition requests to the app tier via the request SQS queue, receive the recognition results from the app tier by polling the response SQS queue and then return the results to the users (`server.py`). The web tier runs on a single t2.micro EC2 instance with an elastic IP, so that the IP address is retained if instance is stopped. The web tier will also implement the autoscaling controller (`controller.py`), which determines how to scale the application tier. The number of the application tier instances are 0 when there are no requests being processed or waiting to be processed and can scale up to 15. Each application tier instance fetches and processes only 1 request at a time. After processing the request, an application tier instance is stopped immediately if there are no more pending requests, otherwise, it continues to process the next request. To reduce the startup overhead, all application tier instances can be initialized to the “stopped” state.

The app tier will use the MTCNN and ResnetV1 for model inference (`face_recognition.py`). The first step is to create an AMI for launching the application tier instances. The base EC2 instance from which the AMI is created will contain the ML model weights and pytorch packages. The app tier instances are named `app-tier-instance-<instance#>`. This prefix is used by the autoscaling process to identify which instances to start. The app tier polls the request queue, fetches the corresponding image from the S3 input bucket, perform model inference for face recognition, stores the recognition result in the S3 output bucket and pushes the recognition result to the response queue. The AMI image should also add the following script in User Data to initialize the `backend.py` process when the instance starts -

```
Content-Type: multipart/mixed; boundary="//"
MIME-Version: 1.0

--//
Content-Type: text/cloud-config; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment;
 filename="cloud-config.txt"

cloud_final_modules:
- [scripts-user, always] 
--//
Content-Type: text/x-shellscript; charset="us-ascii"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Content-Disposition: attachment; filename="userdata.txt"

#!/bin/bash
sudo -u ec2-user -i << 'EOF'
cd /home/ec2-user
nohup python3 backend.py > backend.log 2>&1 &
EOF
--//--
```

To run the project, create a directory `submissions` in autograder with a zip file of web-tier, app-tier and credentials (which contains comma-separated IAM access key, secret key and elastic IP). The IAM user needs the following permissions - IAMReadOnlyAccess, AmazonEC2ReadOnlyAccess, AmazonS3FullAccess, AmazonSQSFullAccess. Now run `python3 autograder.py --num_requests 100 --img_folder="face_images_100" --pred_file="Classification Results on Face Dataset (100 images).csv"
`
The terminal output will show the following -

```
+++++++++++++++++++++++++++++++ CSE546 Autograder  +++++++++++++++++++++++++++++++
- 1) Extract the credentials from the credentials.txt
- 2) Execute the test cases as per the Grading Rubrics
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++++++++++++ Autograder Configurations ++++++++++++++++++++++++++++
Project Path: /Users/sombitroy/Downloads/CSE546-SPRING-2025
Grade Project: Project-1
Class Roster: class_roster.csv
Zip folder path: /Users/sombitroy/Downloads/CSE546-SPRING-2025/submissions
Grading script: /Users/sombitroy/Downloads/CSE546-SPRING-2025/grade_project1_p2.py
Test Image folder path: face_images_1000
Classification results file: Classification Results on Face Dataset (1000 images).csv
Autograder Results: Project-1-grades.csv
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
++++++++++++++++++ Grading for Roy Sombit ASUID: 1232344518 +++++++++++++++++++++
Extracted /Users/sombitroy/Downloads/CSE546-SPRING-2025/submissions/Project1-1232344518-1.zip to extracted
File: extracted/credentials/credentials.txt has values ('AKIARHJJMX2HAD7DVIWY', 'l2U7bQBErOntw2wolaZMEwGqsa53wQRCwKlgavhn', '3.214.42.34')
Credentials parsing complete.
-----------------------------------------------------------------
IAM ACCESS KEY ID: AKIARHJJMX2HAD7DVIWY
IAM SECRET ACCESS KEY: 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
-----------------------------------------------------------------
Following policies are attached with IAM user:cse546-AutoGrader: ['AmazonEC2ReadOnlyAccess', 'IAMReadOnlyAccess', 'AmazonSQSFullAccess', 'AmazonS3FullAccess']
[IAM-log] AmazonEC2ReadOnlyAccess policy attached with grading IAM
[IAM-log] AmazonS3FullAccess policy attached with grading IAM
[IAM-log] AmazonSQSFullAccess policy attached with grading IAM
[Cloudwatch-log] Alarm:Billing alarm with ARN:arn:aws:cloudwatch:us-east-1:084375551630:alarm:Billing alarm found in state:ALARM. It is configued with statistic:Maximum, threshold:1.0 and Comparison Operator:GreaterThanThreshold
[Cloudwatch-log] CAUTION !!! Billing alarm:arn:aws:cloudwatch:us-east-1:084375551630:alarm:Billing alarm is triggered. Release the unwanted resources
-------------- CSE546 Cloud Computing Grading Console -----------
IAM ACCESS KEY ID: AKIARHJJMX2HAD7DVIWY
IAM SECRET ACCESS KEY: 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
Web-Instance IP Address: 3.214.42.34
-----------------------------------------------------------------
----------------- Executing Test-Case:1 ----------------
[EC2-log] AmazonEC2ReadOnlyAccess policy attached with grading IAM
[EC2-log] Found 1 web-tier instances in running state.
[EC2-log] Found 0 app-tier instances in running state
[EC2-log] EC2-state validation Pass. Found 1 web-tier instances in running state. Found 0 app-tier instances in running state.Points deducted: 0
[S3-log] AmazonS3FullAccess policy attached with grading IAM
[S3-log] - WARN: If there are objects in the S3 buckets; they will be deleted
[S3-log] ---------------------------------------------------------
[S3-log] S3 Bucket:1232344518-in-bucket has 0 object(s).
[S3-log] S3 Bucket:1232344518-out-bucket has 0 object(s).
[S3-log] Points deducted:0
[SQS-log] The expectation is that both the Request and Response SQS should exist with max message size set to 1KB and be EMPTY
[SQS-log] - WARN: This will purge any messages available in the SQS
[SQS-log] ---------------------------------------------------------
[SQS-log] AmazonSQSFullAccess policy attached with grading IAM
[SQS-log] SQS Request Queue:1232344518-req-queue has 0 pending messages with max message size set to 1 KB.
[SQS-log] SQS Response Queue:1232344518-resp-queue has 0 pending messages.
[SQS-log] Points deducted:0
----------------- Executing Test-Case:2 ----------------
[AS-log] - Autoscaling validation starts ..
[AS-log] - The expectation is as follows:
[AS-log]  -- # of app tier instances should gradually scale and eventually reduce back to 0
[AS-log]  -- # of SQS messages should gradually increase and eventually reduce back to 0
------------------------------------------------------------------------------------------------------------------
|   # of messages in   |   # of messages in   |   # of app-tier EC2  |  # of objects in S3  |  # of objects in S3  |
|  SQS Request Queue   |  SQS Response Queue  | instances in running |     Input Bucket     |    Output Bucket     |
------------------------------------------------------------------------------------------------------------------
|          0           |          0           |          0           |          0           |          0           |
------------------------------------------------------------------------------------------------------------------
|          0           |          0           |          0           |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|          0           |          0           |          0           |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|          44          |          0           |          3           |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|          36          |          0           |          8           |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|         100          |          0           |          13          |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|         100          |          0           |          15          |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|         100          |          0           |          15          |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|         100          |          0           |          15          |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|          94          |          0           |          15          |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|          94          |          0           |          15          |         100          |          0           |
------------------------------------------------------------------------------------------------------------------
|          87          |          0           |          15          |         100          |          1           |
------------------------------------------------------------------------------------------------------------------
|          82          |          0           |          15          |         100          |          6           |
------------------------------------------------------------------------------------------------------------------
|          79          |          0           |          15          |         100          |          12          |
------------------------------------------------------------------------------------------------------------------
|          75          |          0           |          15          |         100          |          19          |
------------------------------------------------------------------------------------------------------------------
|          72          |          0           |          15          |         100          |          27          |
------------------------------------------------------------------------------------------------------------------
|          65          |          0           |          15          |         100          |          37          |
------------------------------------------------------------------------------------------------------------------
|          51          |          0           |          15          |         100          |          49          |
------------------------------------------------------------------------------------------------------------------
|          33          |          0           |          15          |         100          |          61          |
------------------------------------------------------------------------------------------------------------------
|          33          |          0           |          15          |         100          |          76          |
------------------------------------------------------------------------------------------------------------------
|          7           |          0           |          15          |         100          |          88          |
------------------------------------------------------------------------------------------------------------------
|          7           |          0           |          15          |         100          |         100          |
------------------------------------------------------------------------------------------------------------------
[Workload-gen] ----- Workload Generator Statistics -----
[Workload-gen] Total number of requests: 100
[Workload-gen] Total number of requests completed successfully: 100
[Workload-gen] Total number of failed requests: 0
[Workload-gen] Total number of correct predictions : 100
[Workload-gen] Total number of wrong predictions: 0
[Workload-gen] Total response time: 61.01167416572571 (seconds)
[Workload-gen] -----------------------------------

|          0           |          0           |          0           |         100          |         100          |
------------------------------------------------------------------------------------------------------------------
|          0           |          0           |          0           |         100          |         100          |
------------------------------------------------------------------------------------------------------------------
|          0           |          0           |          0           |         100          |         100          |
------------------------------------------------------------------------------------------------------------------
|          0           |          0           |          0           |         100          |         100          |
------------------------------------------------------------------------------------------------------------------
[Test-Case-3-log] Waiting for 5sec for the resources to scale in ...
[AS-log] Time to scale in to 0 instances: 0.18 seconds.Points:[10/10]
[Test-Case-3-log] Stop event set. Waiting for autoscaling thread to finish.
[Test-Case-3-log] 100/100 entries in S3 bucket:1232344518-in-bucket.Points:[5.0/5]
[Test-Case-3-log] 100/100 entries in S3 bucket:1232344518-out-bucket.Points:[5.0/5]
[Test-Case-3-log] 100/100 correct predictions.Points:[10.0/10]
[Test-Case-3-log] Test Average Latency: 0.610116741657257 sec. `avg latency<1.2s`.Points:[40/40]
[Test-Case-3-log] ---------------------------------------------------------
[AS-log] EC2 instances scale out as expected. Points:[15/15]
[AS-log] EC2 instances scale back to 0 as expected. Points:[5/5]
[AS-log] SQS messages in 1232344518-req-queue increased from 0 and reduced back to 0. Points:[5/5]
[AS-log] SQS messages in 1232344518-resp-queue increased from 0 and reduced back to 0. Points:[5/5]
[AS-log] S3 bucket:1232344518-in-bucket objects increased from 0 to 100.
[S3-log] Bucket:1232344518-in-bucket is now EMPTY !!
[AS-log] S3 bucket:1232344518-out-bucket objects increased from 0 to 100.
[S3-log] Bucket:1232344518-out-bucket is now EMPTY !!
[AS-log] ---------------------------------------------------------
Total Grade Points: 100.0
Removed extracted folder: extracted
Total time taken to grade for Roy Sombit ASUID: 1232344518: 79.90029215812683 seconds
++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
Grading complete for Project-1. Check the Project-1-grades.csv file.
```

