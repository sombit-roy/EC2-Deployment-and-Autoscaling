import boto3
from flask import Flask, request, Response
import os
import json
from collections import deque

app = Flask(__name__)

AWS_REGION = "us-east-1"
S3_BUCKET = "1232344518-in-bucket"
SQS_REQUEST_QUEUE = "1232344518-req-queue"
SQS_RESPONSE_QUEUE = "1232344518-resp-queue"

session = boto3.session.Session()
s3_client = session.client('s3', region_name=AWS_REGION)
sqs_client = session.client('sqs', region_name=AWS_REGION)

request_queue_url = sqs_client.get_queue_url(QueueName=SQS_REQUEST_QUEUE)['QueueUrl']
response_queue_url = sqs_client.get_queue_url(QueueName=SQS_RESPONSE_QUEUE)['QueueUrl']

response_buffer = deque()

@app.route("/", methods=["POST"])
def upload_and_classify():
    if "inputFile" not in request.files:
        return Response("Error: Missing 'inputFile' in request", status=400, mimetype="text/plain")

    file = request.files["inputFile"]
    file_name = file.filename
    item_name = os.path.splitext(file_name)[0]

    s3_client.upload_fileobj(file, S3_BUCKET, file_name)

    sqs_client.send_message(
        QueueUrl=request_queue_url,
        MessageBody=json.dumps({"image_name": file_name})
    )

    while True:
        for i in range(len(response_buffer)):
            message = response_buffer.popleft()
            body = json.loads(message["Body"])

            if body["image_name"] == file_name:
                sqs_client.delete_message(QueueUrl=response_queue_url, ReceiptHandle=message["ReceiptHandle"])
                return Response(f"{item_name}:{body['prediction']}", status=200, mimetype="text/plain")
            else:
                response_buffer.append(message)

        messages = sqs_client.receive_message(
            QueueUrl=response_queue_url,
            MaxNumberOfMessages=10,
            WaitTimeSeconds=2
        )
        
        if "Messages" in messages:
            for message in messages["Messages"]:
                body = json.loads(message["Body"])

                if body["image_name"] == file_name:
                    sqs_client.delete_message(QueueUrl=response_queue_url, ReceiptHandle=message["ReceiptHandle"])
                    return Response(f"{item_name}:{body['prediction']}", status=200, mimetype="text/plain")
                else:
                    response_buffer.append(message)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000, threaded=True)
