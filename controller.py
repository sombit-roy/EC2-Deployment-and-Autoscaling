import boto3

AWS_REGION = "us-east-1"
SQS_REQUEST_QUEUE = "1232344518-req-queue"
S3_OUTPUT_BUCKET = "1232344518-out-bucket"
MAX_INSTANCES = 15
INSTANCE_NAME_PREFIX = "app-tier-instance"

session = boto3.session.Session()
ec2 = session.client('ec2', region_name=AWS_REGION)
sqs = session.client('sqs', region_name=AWS_REGION)
s3 = session.client('s3', region_name=AWS_REGION)

req_queue_url = sqs.get_queue_url(QueueName=SQS_REQUEST_QUEUE)['QueueUrl']

def get_pending_messages(queue_url):
    response = sqs.get_queue_attributes(QueueUrl=queue_url, AttributeNames=["ApproximateNumberOfMessages"])
    return int(response["Attributes"]["ApproximateNumberOfMessages"])

def get_instances_by_state(state):
    response = ec2.describe_instances(
        Filters=[
            {'Name': 'tag:Name', 'Values': [f"{INSTANCE_NAME_PREFIX}-*"]},
            {'Name': 'instance-state-name', 'Values': [state]}
        ]
    )
    return [instance["InstanceId"] for res in response["Reservations"] for instance in res["Instances"]]

def start_instances(num_to_start):
    stopped_instances = get_instances_by_state("stopped")[:num_to_start]

    if stopped_instances:
        for instance_id in stopped_instances:
            ec2.start_instances(InstanceIds=[instance_id])

def stop_idle_instances():
    running_instances = get_instances_by_state("running")
    if running_instances:
        ec2.stop_instances(InstanceIds=running_instances)

while True:
    num_req_messages = get_pending_messages(req_queue_url)
    running_instances = get_instances_by_state("running")
    num_objects = s3.list_objects_v2(Bucket=S3_OUTPUT_BUCKET).get('KeyCount', 0)

    if num_req_messages > 0:
        instances_needed = min(num_req_messages, MAX_INSTANCES) - len(running_instances)
        if instances_needed > 0:
            start_instances(instances_needed)

    elif num_req_messages == 0 and num_objects == 100:
        stop_idle_instances()
