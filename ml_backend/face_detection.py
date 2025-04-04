import json
import cv2
import time
import threading
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from awscrt import mqtt
from awsiot import mqtt_connection_builder
from ml_backend import render_avatar_animation 

# Create a face landmarker instance with the live stream mode:
landmark_results = None

# Default 
color = (0, 255, 0)  # Default: Green

# When True, model will receive requests from AWS
# Only enable when proper files are in your directory
MQTT_TOPIC_ENABLED = False

# AWS IoT Configuration
ENDPOINT = "aevqdnds5bghe-ats.iot.us-east-1.amazonaws.com"
CLIENT_ID = "eoh-processing-unit"
TOPIC = "user-requests"
CERTIFICATE_PATH = "./certificates/eoh-certificate.pem.crt"
PRIVATE_KEY_PATH = "./certificates/eoh-private.pem.key"
ROOT_CA_PATH = "./certificates/AmazonRootCA1.pem"

model_path = "models/face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
FaceLandmarkerResult = mp.tasks.vision.FaceLandmarkerResult
VisionRunningMode = mp.tasks.vision.RunningMode


blendshape_results = []  # Stores all frames' blendshapes
transformation_matrices = []  # Stores transformation matrices
blendShapeData = pd.DataFrame() # Stores all blendshapes in a DataFrame

def print_result(result: FaceLandmarkerResult, output_image: mp.Image, timestamp_ms: int):
    global landmark_results, blendshape_results, transformation_matrices, blendShapeData
    landmark_results = result


    if result.face_blendshapes:
        frame_blendshapes = []  # Stores blendshapes for the current frame
        
        for face_blendshapes in result.face_blendshapes:
            face_data = {blendshape.category_name: blendshape.score for blendshape in face_blendshapes}
            frame_blendshapes.append(face_data)

        blendShapeData = pd.concat([blendShapeData, pd.DataFrame(frame_blendshapes)], ignore_index=True)

        blendshape_results.append(frame_blendshapes)  # Save this frame's blendshapes


# Blendshapes we want to track live
tracked_blendshapes = ["mouthSmileLeft", "eyeBlinkRight", "browInnerUp"]

blendshape_history = {name: [] for name in tracked_blendshapes}
frame_indices = []

# Set up the plot
fig, ax = plt.subplots()

def update_plot(frame):
    global blendShapeData, blendshape_history, frame_indiqces
    # columns = blendShapeData.columns.to_list()
    # print(columns)

    if blendShapeData.empty:
        return

    # Assume each row = one face in one frame
    latest_row = blendShapeData.iloc[-1]

    # Append current frame index
    current_index = frame_indices[-1] + 1 if frame_indices else 0
    frame_indices.append(current_index)

    for name in tracked_blendshapes:
        score = latest_row.get(name, 0.0)
        blendshape_history[name].append(score)

 
    #Clear and replot
    ax.clear()

    # Plot only the latest 100 points for a sliding window effect
    window_size = 100
    for name in tracked_blendshapes:
        y_data = blendshape_history[name][-window_size:]
        x_data = frame_indices[-window_size:]
        ax.plot(x_data, y_data, label=name)

    ax.set_ylim(0, 1)
    ax.set_title("Live Blendshape Graph")
    ax.set_xlabel("Frame")
    ax.set_ylabel("Score")
    ax.legend(loc='upper right')
    plt.tight_layout()

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

def initialize_mqtt_connection():
    mqtt_connection = None
    if MQTT_TOPIC_ENABLED:
        print("Connecting to AWS IoT...")
        mqtt_connection = mqtt_connection_builder.mtls_from_path(
            endpoint=ENDPOINT,
            cert_filepath=CERTIFICATE_PATH,
            pri_key_filepath=PRIVATE_KEY_PATH,
            ca_filepath=ROOT_CA_PATH,
            client_id=CLIENT_ID,
            clean_session=False,
            keep_alive_secs=999
        )
        mqtt_connection.connect()
        print("Connected!")
        mqtt_connection.subscribe(topic=TOPIC, qos=mqtt.QoS.AT_LEAST_ONCE, callback=on_message_received)
        print(f"Subscribed to {TOPIC}")

    return mqtt_connection

def on_message_received(topic, payload, **kwargs):
            global color

            try:
                payload_str = payload.decode("utf-8")  # Decode byte payload to string
                event = json.loads(payload_str)  # Parse JSON string
                print(f"Message received on topic {topic}:")
                print(json.dumps(event, indent=4))

            except json.JSONDecodeError as e:
                print(f"Error decoding JSON: {e}")
            except Exception as e:
                print(f"Unexpected error: {e}")

# Start face landmark detection
def run_face_landmark_detection(cap, options, color=(0, 255, 0)):
    mqtt_connection = initialize_mqtt_connection()

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

    ani = animation.FuncAnimation(fig, update_plot, interval=100)
    plt.ion()  # Enable interactive mode so that plot updates without blocking
    plt.show()

    run_face_landmark_detection(cap, options, color=color)

    render_avatar_animation(blendShapeData)

# Run main function
if __name__ == "__main__":
    main()
    