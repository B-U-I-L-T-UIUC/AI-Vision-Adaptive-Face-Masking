import { FaceLandmarker, FilesetResolver, DrawingUtils } from '@mediapipe/tasks-vision';

let faceLandmarker;
let webcamRunning = false;

const video = document.getElementById('webcam');
const canvas = document.getElementById('output_canvas');
const ctx = canvas.getContext('2d');
const webcamButton = document.getElementById('webcamButton');

async function createFaceLandmarker() {
  const filesetResolver = await FilesetResolver.forVisionTasks(
    'https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm'
  );
  faceLandmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
    baseOptions: {
      modelAssetPath: 'https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task',
      delegate: 'GPU',
    },
    outputFaceBlendshapes: true,
    runningMode: 'VIDEO',
    numFaces: 1,
  });
}

async function enableWebcam() {
  if (webcamRunning) {
    webcamRunning = false;
    webcamButton.innerText = 'Enable Webcam';
    return;
  }

  webcamRunning = true;
  webcamButton.innerText = 'Disable Webcam';

  const constraints = { video: true };
  const stream = await navigator.mediaDevices.getUserMedia(constraints);

  video.srcObject = stream;
  video.addEventListener('loadeddata', predictWebcam);
}

async function predictWebcam() {
  if (!faceLandmarker || !webcamRunning) return;

  canvas.width = video.videoWidth;
  canvas.height = video.videoHeight;

  const startTimeMs = performance.now();
  const results = await faceLandmarker.detectForVideo(video, startTimeMs);

  ctx.clearRect(0, 0, canvas.width, canvas.height);

  if (results.faceLandmarks) {
    const drawingUtils = new DrawingUtils(ctx);
    for (const landmarks of results.faceLandmarks) {
      drawingUtils.drawConnectors(
        landmarks,
        FaceLandmarker.FACE_LANDMARKS_TESSELATION,
        { color: '#C0C0C070', lineWidth: 1 }
      );
      drawingUtils.drawConnectors(
        landmarks,
        FaceLandmarker.FACE_LANDMARKS_RIGHT_EYE,
        { color: '#FF3030' }
      );
      drawingUtils.drawConnectors(
        landmarks,
        FaceLandmarker.FACE_LANDMARKS_LEFT_EYE,
        { color: '#30FF30' }
      );
    }
  }

  if (webcamRunning) {
    requestAnimationFrame(predictWebcam);
  }
}

// Setup
createFaceLandmarker();
webcamButton.addEventListener('click', enableWebcam);
