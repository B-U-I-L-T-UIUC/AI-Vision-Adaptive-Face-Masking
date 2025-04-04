import json
import boto3
import os
import logging
import uuid
import base64
import mimetypes

logger = logging.getLogger()
logger.setLevel("INFO")

# Define the AWS variables
MQTT_TOPIC = "user-requests"
S3_DATA_BUCKET = "eoh-data-bucket"
LOCAL_DOWNLOAD_PATH = "downloads/masks" 

# Initialize AWS clients
iot_client = boto3.client('iot-data', region_name=os.environ.get("AWS_REGION", "us-east-1"))
s3_client = boto3.client("s3")

def download_masks_folder(body, path_params):

    if (body != {}):
        raise ValueError(f"invalid body")   
    
    try:
        # List all files in the /masks folder
        response = s3_client.list_objects_v2(Bucket=S3_DATA_BUCKET, Prefix="masks/")

        if "Contents" not in response:
            payload = {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"no mask files found",
                })
            }
            return (payload, False)
        
        # Generate URLs for each mask file
        mask_urls = [
            f"https://{S3_DATA_BUCKET}.s3.amazonaws.com/{item['Key']}"
            for item in response["Contents"]
        ]

        payload = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "successful",
                "masksUrls" : mask_urls
            })
        }

        return (payload, False)
    
    except Exception as e:
        raise ValueError(f"Error getting files: {str(e)}")

def upload_mask(body, path_params):
    if "fileData" not in body:
        raise ValueError("Missing file data in request body")
    
    if "fileExtension" not in body:
        raise ValueError("Missing file extension in request body")
    
    if "fileName" not in body:
        raise ValueError("Missing file name in request body")

    file_data = body["fileData"]  # Expecting base64-encoded file data
    file_extension = body["fileExtension"]  # File extension should be provided
    file_name = body["fileName"]

    try:
        # Decode the base64 file data
        file_bytes = base64.b64decode(file_data)

        # Generate a unique file name (UUID)
        file_name = f"masks/{file_name}.{file_extension}"

        # Determine the content type (MIME type) based on the file extension
        content_type, _ = mimetypes.guess_type(file_name)
        
        # If the MIME type is unknown, fallback to 'application/octet-stream'
        if not content_type:
            content_type = "application/octet-stream"

        # Upload the file to S3
        s3_client.put_object(
            Bucket=S3_DATA_BUCKET,
            Key=file_name,
            Body=file_bytes,
            ContentType=content_type
        )

        # Generate the URL of the uploaded file
        file_url = f"https://{S3_DATA_BUCKET}.s3.amazonaws.com/{file_name}"
    
        payload = {
            "statusCode": 200,
            "body": json.dumps({
                "message": "File uploaded successfully",
                "fileUrl" : file_url
            })
        }

        return (payload, False)

    except Exception as e:
        raise ValueError(f"Error uploading file: {str(e)}")
    

def upload_image(body, path_params):
    if "userId" not in path_params:
        raise ValueError(f"missing path parameter")
    
    if ("imageData" not in body):
        raise ValueError(f"missing image data")
    
    image_data = body.get("imageData")  # Expecting a base64-encoded string
    file_extension = body.get("fileExtension", "jpg")  # Default to jpg

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

    return (mqtt_payload, True)

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

    return (mqtt_payload, True)

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
    
    return (mqtt_payload, True)

v1_operations = {
    ("POST", "image"): upload_image,
    ("POST", "feature") : feature_change,
    ("GET", "user") : get_user_data,
    ("GET", "mask") : download_masks_folder,
    ("POST", "mask") : upload_mask,
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
                payload, is_mqtt = v1_operations[path](body, path_params)
            else:
                raise ValueError(f"invalid v1 operation: {path}")

        logger.info(f"mqtt payload: {payload}")

        if is_mqtt:
            # Publish the message to the MQTT topic
            logger.info(f"publishing message to mqtt topic: {MQTT_TOPIC}")
            response = iot_client.publish(
                topic=MQTT_TOPIC,
                qos=1, # QoS Level (0: At most once, 1: At least once)
                payload=json.dumps(payload)
            )
        
        if is_mqtt:
            return {
                "statusCode": 200,
                "body": json.dumps({
                    "message": f"Message published to MQTT topic: {MQTT_TOPIC}",
                    "response": response
                })
            }
        
        return payload
    
    except Exception as e:
        logger.exception(e)
        return {
            "statusCode": 500,
            "body": json.dumps({"error": str(e)})
        }