import boto3
import json
import subprocess
import os

AWS_REGION = "us-east-1"
S3_INPUT_BUCKET = "1232344518-in-bucket"
S3_OUTPUT_BUCKET = "1232344518-out-bucket"
SQS_REQUEST_QUEUE = "1232344518-req-queue"
SQS_RESPONSE_QUEUE = "1232344518-resp-queue"

session = boto3.session.Session()
s3_client = session.client('s3', region_name=AWS_REGION)
sqs_client = session.client('sqs', region_name=AWS_REGION)

request_queue_url = sqs_client.get_queue_url(QueueName=SQS_REQUEST_QUEUE)['QueueUrl']
response_queue_url = sqs_client.get_queue_url(QueueName=SQS_RESPONSE_QUEUE)['QueueUrl']

while True:
    messages = sqs_client.receive_message(QueueUrl=request_queue_url, MaxNumberOfMessages=1, WaitTimeSeconds=10)

    if "Messages" in messages:
        message = messages["Messages"][0]
        receipt_handle = message["ReceiptHandle"]
        body = json.loads(message["Body"])
        image_name = body["image_name"]

        image_path = f"/tmp/{image_name}"
        s3_client.download_file(S3_INPUT_BUCKET, image_name, image_path)

        try:
            result = subprocess.check_output(["python3", "face_recognition.py", image_path]).decode("utf-8").strip()
        except subprocess.CalledProcessError as e:
            result = "Unknown"

        s3_client.put_object(Bucket=S3_OUTPUT_BUCKET, Key=image_name, Body=result)

        sqs_client.send_message(
            QueueUrl=response_queue_url,
            MessageBody=json.dumps({"image_name": image_name, "prediction": result})
        )

        sqs_client.delete_message(QueueUrl=request_queue_url, ReceiptHandle=receipt_handle)
