import json
import boto3

def lambda_handler(event, context):
    return {
        "statusCode": 200,
        "body": json.dumps({
            "message": "Hello from Python Lambda!",
            "event": event
        })
    }