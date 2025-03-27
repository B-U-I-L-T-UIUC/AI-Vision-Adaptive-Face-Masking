import json
import cv2
import time
import numpy as np
import mediapipe as mp
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# Create a face landmarker instance with the live stream mode:
landmark_results = None

# Default 
color = (0, 255, 0)  # Default: Green

# When True, model will receive request from AWS
# Only enable when proper files are in your directory
MQTT_TOPIC_ENABLED = False

# AWS IoT Configuration
ENDPOINT = "aevqdnds5bghe-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "eoh-test"
TOPIC = "user-requests"
CERTIFICATE_PATH = "urmom.pem.crt"
PRIVATE_KEY_PATH = "urmom-private.pem.key"
ROOT_CA_PATH = "AmazonRootCA1.pem"
mqtt_connection = None

if MQTT_TOPIC_ENABLED:
    def on_message_received(topic, payload, **kwargs):
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
        keep_alive_secs=30
    )
    mqtt_connection.connect()
    print("Connected!")
    mqtt_connection.subscribe(topic=TOPIC, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received)
    print(f"Subscribed to {TOPIC}")

model_path = "ml_backend/models/face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode

# Face detection
model_path_face_detector = "ml_backend/models/face_detection.task"

FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
VisionRunningMode = mp.tasks.vision.RunningMode


def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global landmark_results
    landmark_results = result

def initialize_face_landmarker(model_path: str):
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result)
    return options

def initialize_camera():
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise Exception("Error: Could not open camera.")
    return cap

# Start face landmark detection
def run_face_landmark_detection(cap, options, color=(0, 255, 0)):
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


# Initialize face detection
def initialize_face_detector(model_path_face_detector: str):
    options = FaceDetectorOptions(
        base_options=BaseOptions(model_asset_path=model_path_face_detector),
        running_mode=VisionRunningMode.IMAGE) 
    return options

# Detect faces and return cropped images 
def face_detection_and_cropping(static_img, options):
    if static_img is None or static_img.size == 0:
        print("Invalid image provided")
        return []
    
    with FaceDetector.create_from_options(options) as face_detector:
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data = static_img)
        face_detector_result = face_detector.detect(mp_image)

    cropped_faces = []  
    if face_detector_result.detections:
        print("No faces detected")
        return cropped_faces
    
    for face in face_detector_result.detections:
        bbox = face.bounding_box
        x, y, w, h = bbox.origin_x, bbox.origin_y, bbox.width, bbox.height
        cropped_face = static_img[y:y+h, x:x+w]
        cropped_faces.append(cropped_face)

    return cropped_faces
        

# Main function
def main():
    cap = initialize_camera()
    options = initialize_face_landmarker(model_path)
    run_face_landmark_detection(cap, options, color=color)

# Run main function
if __name__ == "__main__":
    main()