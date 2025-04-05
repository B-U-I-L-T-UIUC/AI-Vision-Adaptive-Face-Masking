import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import vision from "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3";
import "./FaceMask.css";

const { FaceLandmarker, FilesetResolver } = vision;

const FaceMask = () => {
  const containerRef = useRef(null);
  const raccoonRef = useRef(null);
  const glassesRef = useRef(null);
  const videoRef = useRef(null); 
  const sceneRef = useRef(null);
  const [selectedModel, setSelectedModel] = useState("raccoon");

  useEffect(() => {
    let renderer;
    let scene;
    let camera;
    let faceLandmarker;

    // Initialize FaceLandmarker
    const initFaceLandmarker = async () => {
      const filesetResolver = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@latest/wasm"
      );
      faceLandmarker = await FaceLandmarker.createFromOptions(filesetResolver, {
        baseOptions: {
          modelAssetPath:
            "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
          delegate: "GPU",
        },
        outputFaceBlendshapes: true,
        outputFacialTransformationMatrixes: true,
        runningMode: "VIDEO",
        numFaces: 1,
      });
    };

    // Initialize Three.js Scene
    const initThree = () => {
      if (!renderer) {
        renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000000, 0);
        containerRef.current.appendChild(renderer.domElement);
      }

      if (!scene) {
        scene = new THREE.Scene();
        sceneRef.current = scene;
      }

      if (!camera) {
        camera = new THREE.PerspectiveCamera(80, window.innerWidth / window.innerHeight, 0.01, 100);
        camera.position.z = 2;
      }

      const light = new THREE.AmbientLight(0xffffff, 1.8);
      scene.add(light);
    };

    // Load Models (raccoon and glasses)
    const loadModels = () => {
      const loader = new GLTFLoader();
      
      loader.load("/models/raccoon_head.glb", (gltf) => {
        const raccoon = gltf.scene;
        raccoon.scale.set(0.15, 0.15, 0.15); // Adjust scale to fit on face
        raccoon.visible = false;
        sceneRef.current.add(raccoon);
        raccoonRef.current = raccoon;
      });

      loader.load("/models/glasses.glb", (gltf) => {
        const glasses = gltf.scene;
        glasses.scale.set(0.3, 0.3, 0.3); // Adjust scale to fit on face
        glasses.visible = false;
        sceneRef.current.add(glasses);
        glassesRef.current = glasses;
      });
    };

    const applyMatrixToModels = (matrixData) => {
      if (!matrixData || matrixData.length === 0) return;
    
      const threeMatrix = new THREE.Matrix4();
      threeMatrix.fromArray(matrixData);
      const position = new THREE.Vector3();
      const quaternion = new THREE.Quaternion();
      const scale = new THREE.Vector3();
      threeMatrix.decompose(position, quaternion, scale);
      // position.multiplyScalar(0.20);
      // scale.set(10,10,10);
    
      console.log(position)
      console.log(quaternion)
      // Fix: Scale down translation from mm to meters
      // position.multiplyScalar(0.20); // Adjust this factor if needed
    
      // Optionally offset the Y and Z if needed
      position.y += 0.05;
      position.z += 0.02;

      // position.x *= -1;
      // quaternion.x *= -1;
      // quaternion.y *= -1;
      // quaternion.z *= -1;
      // position.multiplyScalar(1.5);

    
      if (raccoonRef.current) {
        raccoonRef.current.position.copy(position);
        raccoonRef.current.quaternion.copy(quaternion);
        raccoonRef.current.scale.set(60, 60, 60); // Match model scale
        raccoonRef.current.visible = true;
      }
    
      if (glassesRef.current) {
        glassesRef.current.position.copy(position);
        glassesRef.current.quaternion.copy(quaternion);
        glassesRef.current.scale.set(0.3, 0.3, 0.3);
        glassesRef.current.visible = true;
      }
    };
    
    
    const processResults = (results) => {
      if (!results || !results.faceLandmarks || !results.faceLandmarks.length) return;
    
       let landmarks = results.faceLandmarks[0].map(lm => ({
        x: lm.x,
        y: lm.y,
        z: lm.z,
      }));
    
      const blendshapes = {};
      for (const category of results.faceBlendshapes[0]?.categories || []) {
        if (category && category.categoryName && category.score !== undefined) {
          blendshapes[category.categoryName] = category.score;
        }
      }

      let matrixData = results.facialTransformationMatrixes[0]?.data;
      console.log("Matrix frame:", JSON.stringify(matrixData));
      applyMatrixToModels(matrixData);

      [raccoonRef.current, glassesRef.current].forEach((model) => {

        if (model) {
          model.visible = true;
          model.traverse((obj) => {
            if (obj.isMesh && obj.morphTargetDictionary && obj.morphTargetInfluences) {
              for (const [name, value] of Object.entries(blendshapes)) {
                const index = obj.morphTargetDictionary[name];
                if (index !== undefined) {
                  obj.morphTargetInfluences[index] = value;
                }
              }
            }
          });
        }
      });
      
    };
    
    

    // Track Face function using video input
    const trackFace = async () => {
      if (videoRef.current && faceLandmarker) {
        const results = await faceLandmarker.detectForVideo(
          videoRef.current, 
          performance.now());
        // console.log(results);
        processResults(results);
      }
      requestAnimationFrame(trackFace);
    };

    const animate = () => {
      // model.visible = model === getSelectedModel();
      requestAnimationFrame(animate);
      if (sceneRef.current && camera) {
        renderer.render(sceneRef.current, camera);
      }
    };
    

    const getSelectedModel = () => {
      return selectedModel === "raccoon" ? raccoonRef.current : glassesRef.current;
    };

    const setup = async () => {
      initThree();
      initFaceLandmarker();
      loadModels();
      animate();
      navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1280 },
          height: { ideal: 720 },
          facingMode: "user" // "user" for front camera, "environment" for back
        }
      })
      navigator.mediaDevices.getUserMedia({
        video: {
          width: { ideal: 1920 },
          height: { ideal: 1080 },
          facingMode: "user" // "user" for front camera, "environment" for back
      } }).then((stream) => {
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
          videoRef.current.onplaying = () => {
            trackFace();
            animate();
          };
        }
      });
    };

    setup();

    return () => {};
  }, [selectedModel]);

  return (
    <>
      <video ref={videoRef} className="video-background" autoPlay muted playsInline></video>
      <div ref={containerRef} className="canvas-container" />
    </>
  );
};

export default FaceMask;
