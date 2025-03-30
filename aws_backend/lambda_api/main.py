import json
import boto3
import os
import logging
import uuid
import base64

logger = logging.getLogger()
logger.setLevel("INFO")

# Define the AWS variables
MQTT_TOPIC = "user-requests"
S3_DATA_BUCKET = "eoh-data-bucket"

# Initialize AWS clients
iot_client = boto3.client('iot-data', region_name=os.environ.get("AWS_REGION", "us-east-1"))
s3_client = boto3.client("s3")

def upload_image(body, path_params):
    if "userId" not in path_params:
        raise ValueError(f"missing path parameter")
    
    if ("image_data" not in body):
        raise ValueError(f"missing image data")
    
    image_data = body.get("image_data")  # Expecting a base64-encoded string
    file_extension = body.get("file_extension", "jpg")  # Default to jpg

    image_bytes = base64.b64decode(image_data)
    file_name = f"{uuid.uuid4()}.{file_extension}"

    s3_client.put_object(
        Bucket=S3_DATA_BUCKET,
        Key=file_name,
        Body=image_bytes,
        ContentType=f"image/{file_extension}"
    )

    image_url = f"https://{S3_DATA_BUCKET}.s3.amazonaws.com/{file_name}"

    mqtt_payload = {
        "userId" : path_params["userId"],
        "requestType" : "upload-image",
        "event" : {
            "imageUrl" : image_url,
        }
    }

    return mqtt_payload

def feature_change(body, path_params):
    if "userId" not in path_params:
        raise ValueError(f"missing path parameter")
    
    if ("feature" not in body or
        "featureParam" not in body):
        raise ValueError(f"missing body parameter")

    mqtt_payload = {
        "userId" : path_params["userId"],
        "requestType" : "feature-change",
        "event" : {
            "feature" : body["feature"],
            "featureParam" : body["featureParam"]
        }
    }

    return mqtt_payload

def get_user_data(body, path_params):
    if "userId" not in path_params:
        raise ValueError(f"missing path parameter")
    
    if (body != {}):
        raise ValueError(f"invalid body")

    mqtt_payload = {
        "userId" : path_params["userId"],
        "requestType" : "get-user-data",
        "event" : {}
    }
    
    return mqtt_payload

v1_operations = {
    ("POST", "image"): upload_image,
    ("POST", "feature") : feature_change,
    ("GET", "user") : get_user_data,
}

def lambda_handler(event, context):
    """
    AWS Lambda handler function to publish a message to an MQTT topic in AWS IoT Core from API requests.
    """

    resource_path = event["resource"].split("/")
    method_type = event["httpMethod"]

    path_params = event.get("pathParameters", {})
    body = json.loads(event.get("body") or "{}")

    try:
        # v1 paths
        logger.info("attemping v1 paths")
        path = (method_type, resource_path[2])
        if resource_path[1] == "v1":
            if (method_type, resource_path[2]) in v1_operations:
                mqtt_payload = v1_operations[path](body, path_params)
            else:
                raise ValueError(f"invalid v1 operation: {path}")

        logger.info(f"mqtt payload: {mqtt_payload}")

        # Publish the message to the MQTT topic
        logger.info(f"publishing message to mqtt topic: {MQTT_TOPIC}")
        response = iot_client.publish(
            topic=MQTT_TOPIC,
            qos=1,  # QoS Level (0: At most once, 1: At least once)
            payload=json.dumps(mqtt_payload)
        )

        return {
            "statusCode": 200,
            "body": json.dumps({
                "message": f"Message published to MQTT topic: {MQTT_TOPIC}",
                "response": response
            })
        }
    
    except Exception as e:
        logger.exception(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }