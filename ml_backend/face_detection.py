import json
import cv2
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
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

model_path = "models/face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


blendshape_results = []  # Stores all frames' blendshapes
transformation_matrices = []  # Stores transformation matrices

def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global landmark_results, blendshape_results, transformation_matrices
    landmark_results = result

    if result.face_blendshapes:
        frame_blendshapes = []  # Stores blendshapes for the current frame
        
        for face_blendshapes in result.face_blendshapes:
            face_data = {blendshape.category_name: blendshape.score for blendshape in face_blendshapes}
            frame_blendshapes.append(face_data)

        blendshape_results.append(frame_blendshapes)  # Save this frame's blendshapes

        # 🔹 Print blendshapes for debugging (Top 5 for each face)
        print(f"\nFrame {len(blendshape_results)} Blendshapes:")
        for i, face_data in enumerate(frame_blendshapes):
            sorted_blendshapes = sorted(face_data.items(), key=lambda x: x[1], reverse=True)[:5]  # Top 5
            print(f"Face {i}: " + ", ".join(f"{k}: {v:.2f}" for k, v in sorted_blendshapes))

    if result.facial_transformation_matrixes:
        transformation_matrices.append(result.facial_transformation_matrixes)
        print("\nFacial Transformation Matrices:")
        for i, matrix in enumerate(result.facial_transformation_matrixes):
            print(f"Face {i} Matrix:\n{np.array(matrix)}\n")  # Pretty-print matrix
    

def initialize_face_landmarker(model_path: str):
    options = FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=model_path),
        running_mode=VisionRunningMode.LIVE_STREAM,
        result_callback=print_result,
        output_face_blendshapes=True,
        output_facial_transformation_matrixes=True 
    )
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

            # Display facial blendshapes in OpenCV overlay
            if landmark_results and landmark_results.face_blendshapes:
                for i, face_blendshapes in enumerate(landmark_results.face_blendshapes):
                    y_offset = 20
                    for blendshape in face_blendshapes[:5]:  # Show top 5 blendshapes
                        text = f"{blendshape.category_name}: {blendshape.score:.2f}"
                        cv2.putText(frame, text, (10, y_offset), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
                        y_offset += 20

            cv2.imshow('MediaPipe Face Detection', frame)

            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()


if MQTT_TOPIC_ENABLED and mqtt_connection:
    print("Disconnecting...")
    mqtt_connection.disconnect().result()
    print("Disconnected from AWS IoT.")


# Main function
def main():
    cap = initialize_camera()
    options = initialize_face_landmarker(model_path)
    run_face_landmark_detection(cap, options, color=color)

# Run main function
if __name__ == "__main__":
    main()