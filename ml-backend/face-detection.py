import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import cv2 
import time
import numpy as np

model_path = "models/blaze_face_short_range.tflite"

BaseOptions = mp.tasks.BaseOptions
FaceDetector = mp.tasks.vision.FaceDetector
FaceDetectorOptions = mp.tasks.vision.FaceDetectorOptions
FaceDetectorResult = mp.tasks.vision.FaceDetectorResult
VisionRunningMode = mp.tasks.vision.RunningMode

detection_results = None

# Create a face detector instance with the live stream mode:
def print_result(result: FaceDetectorResult, output_image: mp.Image, timestamp_ms: int):
    global detection_results
    detection_results = result

options = FaceDetectorOptions(
    base_options=BaseOptions(model_asset_path='models/blaze_face_short_range.tflite'),
    running_mode=VisionRunningMode.LIVE_STREAM,
    result_callback=print_result)

cap = cv2.VideoCapture(0)

if not cap.isOpened():
    print("Cannot open camera")
    exit()

with FaceDetector.create_from_options(options) as detector:
  # The detector is initialized. Use it here.
  while cap.isOpened():
    ret, frame = cap.read()
    if not ret:
        print("Ignoring empty camera frame.")
        continue

    numpy_frame_from_opencv = np.array(frame)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=numpy_frame_from_opencv)

    frame_timestamp_ms = int(time.time() * 1000)
    detector.detect_async(mp_image, frame_timestamp_ms)

    # If faces are detected, draw bounding boxed.
    if detection_results and detection_results.detections:
        for detection in detection_results.detections:
            bbox = detection.bounding_box
            x1, y1 = int(bbox.origin_x), int(bbox.origin_y)
            x2, y2 = x1 + int(bbox.width), y1 + int(bbox.height)

            # Draw red bounding box around the face
            cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 0, 255), 2)

    cv2.imshow('MediaPipe Face Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
      break

cap.release()
cv2.destroyAllWindows()
