import json
import cv2
import time
import numpy as np
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
from awscrt import mqtt
from awsiot import mqtt_connection_builder

# Global variables and configuration
landmark_results = None
color = (0, 255, 0)
MQTT_TOPIC_ENABLED = False

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
        frame_blendshapes = []
        for face_blendshapes in result.face_blendshapes:
            face_data = {blendshape.category_name: blendshape.score for blendshape in face_blendshapes}
            frame_blendshapes.append(face_data)
        blendshape_results.append(frame_blendshapes)
        print(f"\nFrame {len(blendshape_results)} Blendshapes:")
        for i, face_data in enumerate(frame_blendshapes):
            sorted_blendshapes = sorted(face_data.items(), key=lambda x: x[1], reverse=True)[:5]
            print(f"Face {i}: " + ", ".join(f"{k}: {v:.2f}" for k, v in sorted_blendshapes))

    if result.facial_transformation_matrixes:
        transformation_matrices.append(result.facial_transformation_matrixes)
        print("\nFacial Transformation Matrices:")
        for i, matrix in enumerate(result.facial_transformation_matrixes):
            print(f"Face {i} Matrix:\n{np.array(matrix)}\n")

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

def preprocess_avatar(avatar_img):
    """
    If the avatar image has an alpha channel, remove transparent margins by
    cropping to the nonzero alpha region.
    """
    if avatar_img.shape[2] == 4:
        alpha = avatar_img[:, :, 3]
        coords = cv2.findNonZero(alpha)
        if coords is not None:
            x, y, w, h = cv2.boundingRect(coords)
            cropped = avatar_img[y:y+h, x:x+w]
            return cropped
    return avatar_img

def run_face_landmark_detection(cap, options, color=(0, 255, 0), draw_landmarks=False):
    # Load your avatar image (ensure the path is correct)
    avatar_image = cv2.imread("bear.png", cv2.IMREAD_UNCHANGED) 
    if avatar_image is None:
        print("Error: Avatar image not found.")
        return

    # Preprocess the avatar image: crop out any transparent margins
    avatar_preprocessed = preprocess_avatar(avatar_image)

    with FaceLandmarker.create_from_options(options) as landmarker:
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                print("Ignoring empty camera frame.")
                continue

            # Process frame for face detection
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=frame_rgb)
            frame_timestamp_ms = int(time.time() * 1000)
            landmarker.detect_async(mp_image, frame_timestamp_ms)

            # Optionally draw landmarks for debugging
            if draw_landmarks and landmark_results and landmark_results.face_landmarks:
                for face_landmarks in landmark_results.face_landmarks:
                    pts = [(int(l.x * frame.shape[1]), int(l.y * frame.shape[0])) for l in face_landmarks]
                    for (x, y) in pts:
                        cv2.circle(frame, (x, y), 1, color, -1)

            # Process each detected face
            if landmark_results and landmark_results.face_landmarks:
                for face_landmarks in landmark_results.face_landmarks:
                    # Compute a bounding box covering all landmarks:
                    pts = [(int(l.x * frame.shape[1]), int(l.y * frame.shape[0])) for l in face_landmarks]
                    face_x = min(p[0] for p in pts)
                    face_y = min(p[1] for p in pts)
                    face_width = max(p[0] for p in pts) - face_x
                    face_height = max(p[1] for p in pts) - face_y

                    if face_width <= 0 or face_height <= 0:
                        print("Invalid face dimensions, skipping.")
                        continue

                    # Resize the preprocessed avatar to exactly match the face bounding box
                    avatar_scaled = cv2.resize(avatar_preprocessed, (face_width, face_height), interpolation=cv2.INTER_AREA)

                    # Get the region of interest (ROI) from the frame where the face is
                    roi = frame[face_y:face_y+face_height, face_x:face_x+face_width]

                    # If the avatar has an alpha channel, perform proper alpha blending
                    if avatar_scaled.shape[2] == 4:
                        # Separate color and alpha channels
                        avatar_rgb = avatar_scaled[:, :, :3].astype(float)
                        avatar_alpha = avatar_scaled[:, :, 3].astype(float) / 255.0  # normalized alpha
                        # Make sure alpha has three channels
                        avatar_alpha = cv2.merge([avatar_alpha, avatar_alpha, avatar_alpha])
                        
                        roi = roi.astype(float)
                        blended = avatar_alpha * avatar_rgb + (1 - avatar_alpha) * roi
                        blended = blended.astype(np.uint8)
                        frame[face_y:face_y+face_height, face_x:face_x+face_width] = blended
                    else:
                        # If no alpha channel, simply overlay
                        frame[face_y:face_y+face_height, face_x:face_x+face_width] = avatar_scaled

            cv2.imshow('MediaPipe Face Detection with Avatar', frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    cap.release()
    cv2.destroyAllWindows()




if MQTT_TOPIC_ENABLED and mqtt_connection:
    print("Disconnecting...")
    mqtt_connection.disconnect().result()
    print("Disconnected from AWS IoT.")

def main():
    cap = initialize_camera()
    options = initialize_face_landmarker(model_path)
    run_face_landmark_detection(cap, options, color=color, draw_landmarks=False)

if __name__ == "__main__":
    main()
