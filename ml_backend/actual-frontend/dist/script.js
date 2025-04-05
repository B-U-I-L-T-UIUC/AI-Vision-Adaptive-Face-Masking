import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import vision from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3";

const { FaceLandmarker, FilesetResolver } = vision;

const containerRef = document.getElementById("canvas-container");
const videoRef = document.getElementById("webcam");

let renderer, scene, camera, faceLandmarker, maskModel;

async function initFaceLandmarker() {
  const filesetResolver = await FilesetResolver.forVisionTasks(
    "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
  );
  faceLandmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
    baseOptions: {
      modelAssetPath:
        "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
      delegate: "GPU",
    },
    outputFaceBlendshapes: true,
    outputTransformationMatrixes: true,
    runningMode: "VIDEO",
    numFaces: 1,
  });
}

// function initThree() {
//   renderer = new THREE.WebGLRenderer({ alpha: true });
//   renderer.setSize(window.innerWidth, window.innerHeight);
//   containerRef.appendChild(renderer.domElement);

//   scene = new THREE.Scene();

//   camera = new THREE.PerspectiveCamera(
//     80,
//     window.innerWidth / window.innerHeight,
//     0.01,
//     100
//   );
//   camera.position.z = 2;

//   const light = new THREE.AmbientLight(0xffffff, 1.8);
//   scene.add(light);

//   loadModel();
// }

// function loadModel() {
//   const loader = new GLTFLoader();
//   loader.load(
//     "/raccoon_head.glb",
//     (gltf) => {
//       maskModel = gltf.scene;
//       maskModel.scale.set(50, 50, 50);
//       scene.add(maskModel);
//     },
//     undefined,
//     (error) => console.error("Mask model load error:", error)
//   );
// }

function updateMaskPosition(landmarks) {
  if (!maskModel || !landmarks.length) return;
  const noseTip = landmarks[1];
  maskModel.position.set(noseTip.x - 0.5, -noseTip.y + 0.5, -noseTip.z);
}

function animate() {
  requestAnimationFrame(animate);
  renderer.render(scene, camera);
}

async function startFaceTracking(videoElement) {
  await initFaceLandmarker();
  async function trackFace() {
    if (!faceLandmarker) return;
    const results = faceLandmarker.detectForVideo(
      videoElement,
      performance.now()
    );

    if (results.faceLandmarks?.length) {
      updateMaskPosition(results.faceLandmarks[0]);
    }

    if (results.faceBlendshapes?.length) {
      const blendshapes = {};
      for (const bs of results.faceBlendshapes[0]) {
        blendshapes[bs.categoryName] = bs.score;
      }
      console.log("Blendshapes:", blendshapes);
    }

    if (results.facialTransformationMatrixes?.length) {
      const matrix = Array.from(results.facialTransformationMatrixes[0].data);
      const reshaped = [];
      for (let i = 0; i < 4; i++) {
        reshaped.push(matrix.slice(i * 4, (i + 1) * 4));
      }
      console.log("Transformation matrix:", reshaped);
    }

    requestAnimationFrame(trackFace);
  }
  trackFace();
}

function main() {
  initThree();
  animate();

  navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
    if (videoRef) {
      videoRef.srcObject = stream;
      videoRef.addEventListener("loadeddata", () =>
        startFaceTracking(videoRef)
      );
    }
  });
}

window.onload = main;
