import json
import boto3
import os

### Needed endpoints ###
# Image upload 
#   POST /image/{userId}
# User avatar feature change
#   POST /feature/{userId}
# Get user data from ml backend
#   GET /user/{userId}

### Message Payload Structure ###
# This message payload will be sent to and proccessed by the ml backend
# {
#     "requestId" : context.aws_request_id,
#     "userId" : userId,
#     "requestType" : requestType,
#     "event" : specifiedEvent,
# }

### image upload specifiedEvent ###
# {
#     "imageURL" : s3ImageUrl,
# }

### avatar feature change specifiedEvent ###
# {
#     "feature" : feature
#     "{feature}" : featureParam
# }


# Initialize AWS IoT Data client
iot_client = boto3.client('iot-data', region_name=os.environ.get("AWS_REGION", "us-east-1"))

# Define the MQTT topic
MQTT_TOPIC = "user-requests"

def lambda_handler(event, context):
    """
    AWS Lambda handler function to publish a message to an MQTT topic in AWS IoT Core.
    """

    resource_path = event["resource"].split("/")
    method_type = event["httpMethod"]

    try:

        if resource_path[1] == "v1":
            if method_type == "POST" and resource_path[2] == "image":
                pass
            if method_type == "POST" and resource_path[2] == "feature":
                pass
            if method_type == "GET" and resource_path[2] == "user":
                pass
        
        # Construct the message payload
        # message_payload = {
        #     "requestId": context.aws_request_id,
        #     "color": event["pathParameters"]["color"],
        #     "event": event["body"]
        # }

        # Publish the message to the MQTT topic
        # response = iot_client.publish(
        #     topic=MQTT_TOPIC,
        #     qos=1,  # QoS Level (0: At most once, 1: At least once)
        #     payload=json.dumps(message_payload)
        # )

        # return {
        #     "statusCode": 200,
        #     "body": json.dumps({
        #         "message": f"Message published to MQTT topic: {MQTT_TOPIC}",
        #         "response": response
        #     })
        # }
    
        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"successfully hit lambda function",
                "resource_path": resource_path,
                "method_type": method_type
            })
        }

    except Exception as e:
        print(f"Error publishing to MQTT: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }