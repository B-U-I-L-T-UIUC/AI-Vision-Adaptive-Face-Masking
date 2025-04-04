import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import "../styles/FaceMask.css";

const FaceMask = () => {
  const containerRef = useRef(null);
  const maskRef = useRef(null);
  const sceneRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState("raccoon");

  useEffect(() => {
    let renderer, scene, camera;

    const initThree = () => {
      renderer = new THREE.WebGLRenderer({ alpha: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setClearColor(0x000000, 0);
      containerRef.current.appendChild(renderer.domElement);

      scene = new THREE.Scene();
      sceneRef.current = scene;

      camera = new THREE.PerspectiveCamera(80, window.innerWidth / window.innerHeight, 0.01, 100);
      camera.position.z = 2;

      const light = new THREE.AmbientLight(0xffffff, 1.8);
      scene.add(light);
    };

    const loadModel = () => {
      const loader = new GLTFLoader();
      loader.load(
        `/models/raccoon_head.glb`,
        (gltf) => {
          const mask = gltf.scene;
          mask.scale.set(3, 3, 3);
          sceneRef.current.add(mask);
          maskRef.current = mask;
        },
        undefined,
        (error) => console.error("Model load error:", error)
      );
    };

    const applyLandmarksToMask = (landmarks) => {
      if (!maskRef.current || !landmarks) return;

      const noseTip = landmarks[1];
      maskRef.current.position.set(noseTip.x - 0.5, -noseTip.y + 0.5, -noseTip.z);
      maskRef.current.rotation.set(0, Math.atan2(noseTip.x, noseTip.z), 0);
    };

    const setupFaceTracking = async () => {
      const vision = await import("https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3");
      const { FaceLandmarker, FilesetResolver } = vision;

      const filesetResolver = await FilesetResolver.forVisionTasks();
      const faceLandmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
        baseOptions: { modelAssetPath: "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task" },
        outputFaceBlendshapes: false,
        runningMode: "VIDEO",
        numFaces: 1,
      });

      const video = document.createElement("video");
      navigator.mediaDevices.getUserMedia({ video: true }).then((stream) => {
        video.srcObject = stream;
        video.play();
        requestAnimationFrame(detectFace);
      });

      const detectFace = async () => {
        const results = faceLandmarker.detectForVideo(video, performance.now());
        if (results.faceLandmarks.length) {
          applyLandmarksToMask(results.faceLandmarks[0]);
        }
        requestAnimationFrame(detectFace);
      };
    };

    const animate = () => {
      requestAnimationFrame(animate);
      if (sceneRef.current && camera) {
        renderer.render(sceneRef.current, camera);
      }
    };

    const setup = () => {
      initThree();
      loadModel();
      setupFaceTracking();
      animate();
    };

    setup();
    return () => { renderer.dispose(); };
  }, [selectedModel]);

  return (
    <>
      <div ref={containerRef} className="canvas-container" />
      <div className="dropzone" onDragOver={(e) => e.preventDefault()} onDrop={(e) => {
        const model = e.dataTransfer.getData("raccoon_head");
        if (model) setSelectedModel(model);
      }}>
        Drop here to change model
      </div>
    </>
  );
};

export default FaceMask;
