import cv2
import json
import time
import asyncio
import threading
import numpy as np
from fastapi import FastAPI, WebSocket
from fastapi.responses import StreamingResponse
from starlette.middleware.cors import CORSMiddleware
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import uvicorn
from starlette.websockets import WebSocketDisconnect
from fastapi import WebSocketDisconnect

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# === Mediapipe Setup ===
model_path = "models/face_landmarker.task"

BaseOptions = mp.tasks.BaseOptions
FaceLandmarker = mp.tasks.vision.FaceLandmarker
FaceLandmarkerOptions = mp.tasks.vision.FaceLandmarkerOptions
VisionRunningMode = mp.tasks.vision.RunningMode

options = FaceLandmarkerOptions(
    base_options=BaseOptions(model_asset_path=model_path),
    running_mode=VisionRunningMode.VIDEO,
    output_face_blendshapes=True,
    output_facial_transformation_matrixes=True
)
landmarker = FaceLandmarker.create_from_options(options)

latest_frame = None

def capture_loop():
    global latest_frame
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        raise RuntimeError("❌ Could not open webcam!")

    while True:
        ret, frame = cap.read()
        if ret:
            latest_frame = cv2.flip(frame, 1)

threading.Thread(target=capture_loop, daemon=True).start()

def mjpeg_generator():
    global latest_frame
    while True:
        if latest_frame is not None:
            _, jpeg = cv2.imencode(".jpg", latest_frame)
            frame_bytes = jpeg.tobytes()

            yield (
                b"--frame\r\n"
                b"Content-Type: image/jpeg\r\n\r\n" +
                frame_bytes +
                b"\r\n"
            )
        time.sleep(0.03)

@app.get("/video")
async def video_feed():
    return StreamingResponse(mjpeg_generator(), media_type="multipart/x-mixed-replace; boundary=frame")



@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    print("🔗 WebSocket connected")

    try:
        while True:
            if latest_frame is not None:
                # If frame exists, send immediately
                rgb = cv2.cvtColor(latest_frame, cv2.COLOR_BGR2RGB)
                mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
                timestamp = int(time.time() * 1000)

                result = landmarker.detect_for_video(mp_image, timestamp)

                landmarks = []
                blendshapes = {}
                matrix = []

                if result.face_landmarks:
                    landmarks = [{"x": lm.x, "y": lm.y, "z": lm.z} for lm in result.face_landmarks[0]]

                if result.face_blendshapes:
                    for bs in result.face_blendshapes[0]:
                        blendshapes[bs.category_name] = bs.score

                if result.facial_transformation_matrixes:
                    raw = np.array(result.facial_transformation_matrixes[0].data).reshape(4, 4)
                    matrix = raw.tolist()

                data = {
                    "landmarks": landmarks,
                    "blendshapes": blendshapes,
                    "matrix": matrix
                }

                await websocket.send_text(json.dumps(data))
            
            await asyncio.sleep(0.01)  # smaller sleep so we don't spam CPU

    except WebSocketDisconnect:
        print("⚪️ Client disconnected. Waiting for next...")

    except Exception as e:
        print(f"⚠️ Unexpected error: {e}")

    finally:
        try:
            await websocket.close()
        except Exception:
            pass

if __name__ == "__main__":
    print("✅ Backend running at http://localhost:8000")
    uvicorn.run(app, host="0.0.0.0", port=8000)