import json
import cv2
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from awscrt import mqtt
from awsiot import mqtt_connection_builder

model_path = "models/face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Create a face landmarker instance with the live stream mode:
landmark_results = None

# Default 
color = (0, 255, 0)  # Default: Green

# When True, model will receive request from AWS
# Only enable when proper files are in your directory
MQTT_TOPIC_ENABLED = True

# AWS IoT Configuration
ENDPOINT = "aevqdnds5bghe-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "eoh-processing-unit"
TOPIC = "user-requests"
CERTIFICATE_PATH = "./certificates/eoh-certificate.pem.crt"
PRIVATE_KEY_PATH = "./certificates/eoh-private.pem.key"
ROOT_CA_PATH = "./certificates/AmazonRootCA1.pem"
mqtt_connection = None

if MQTT_TOPIC_ENABLED:
    print("TRYING TO CONNECT")
    def on_message_received(topic, payload, **kwargs):
        print("RECEIVED MESSAGE")
        global color
        print(f"Message received on topic {topic}: {payload}")
        try:
            event = json.loads(payload)
            if "color" in event:
                if event["color"] == "red":
                    color = (0, 0, 255)
                elif event["color"] == "blue":
                    color = (255, 0, 0)
                elif event["color"] == "green":
                    color = (0, 255, 0)
                print(f"Updated bounding box color: {color}")
        except json.JSONDecodeError:
            print("Error decoding JSON message")

    print("Connecting to AWS IoT...")
    mqtt_connection = mqtt_connection_builder.mtls_from_path(
        endpoint=ENDPOINT,
        cert_filepath=CERTIFICATE_PATH,
        pri_key_filepath=PRIVATE_KEY_PATH,
        ca_filepath=ROOT_CA_PATH,
        client_id=CLIENT_ID,
        clean_session=False,
        keep_alive_secs=180
    )
    mqtt_connection.connect()
    print("Connected!")
    mqtt_connection.subscribe(topic=TOPIC, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received)
    print(f"Subscribed to {TOPIC}")

    subscribe_future, _ = mqtt_connection.subscribe(
    topic=TOPIC,
    qos=mqtt.QoS.AT_LEAST_ONCE,
    callback=on_message_received
    )

    try:
        subscribe_result = subscribe_future.result(timeout=5)  # Wait for confirmation
        print(f"Successfully subscribed: {subscribe_result}")
    except Exception as e:
        print(f"Subscription failed: {e}")

def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global landmark_results
    landmark_results = result

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

# Start face landmark detection
with FaceLandmarker.create_from_options(options) as landmarker:
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            print("Ignoring empty camera frame.")
            continue

        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
        frame_timestamp_ms = int(time.time() * 1000)
        landmarker.detect_async(mp_image, frame_timestamp_ms)
        time.sleep(0.01)

        # Draw landmarks if detected
        if landmark_results and landmark_results.face_landmarks:
            for face_landmarks in landmark_results.face_landmarks:
                for landmark in face_landmarks:
                    x, y = int(landmark.x * frame.shape[1]), int(landmark.y * frame.shape[0])
                    cv2.circle(frame, (x, y), 1, color, -1)  # Draw dots for landmarks

        cv2.imshow('MediaPipe Face Detection', frame)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

cap.release()
cv2.destroyAllWindows()

if MQTT_TOPIC_ENABLED and mqtt_connection:
    print("Disconnecting...")
    mqtt_connection.disconnect().result()
    print("Disconnected from AWS IoT.")