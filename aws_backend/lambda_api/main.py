import json
import boto3
import os

# Initialize AWS IoT Data client
iot_client = boto3.client('iot-data', region_name=os.environ.get("AWS_REGION", "us-east-1"))

# Define the MQTT topic
MQTT_TOPIC = "user-requests"

def lambda_handler(event, context):
    """
    AWS Lambda handler function to publish a message to an MQTT topic in AWS IoT Core.
    """
    try:
        # Construct the message payload
        message_payload = {
            "requestId": context.aws_request_id,
            "color": event["pathParameters"]["color"],
            "event": event["body"]
        }

        # Publish the message to the MQTT topic
        response = iot_client.publish(
            topic=MQTT_TOPIC,
            qos=1,  # QoS Level (0: At most once, 1: At least once)
            payload=json.dumps(message_payload)
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Message published to MQTT topic: {MQTT_TOPIC}",
                "response": response
            })
        }

    except Exception as e:
        print(f"Error publishing to MQTT: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }