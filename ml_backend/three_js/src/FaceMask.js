// FaceMask.jsx
import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import mqtt from "mqtt";
import "./FaceMask.css";

export default function FaceMask() {
  const containerRef = useRef(null);
  const videoRef = useRef(null);
  const modelRef = useRef(null);
  const [debugData, setDebugData] = useState({});
  const [modelLoaded, setModelLoaded] = useState(false);

  useEffect(() => {
    let renderer, scene, camera;
    let socket;
    let client;
    let animationFrameId;

    const initThree = () => {
      renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
      renderer.setSize(window.innerWidth, window.innerHeight);
      renderer.setPixelRatio(window.devicePixelRatio);
      containerRef.current.appendChild(renderer.domElement);

      scene = new THREE.Scene();

      camera = new THREE.PerspectiveCamera(60, window.innerWidth / window.innerHeight, 0.01, 10); 
      camera.position.z = 1.5;
      scene.add(camera);

      const ambientLight = new THREE.AmbientLight(0xffffff, 1.5);
      scene.add(ambientLight);

      const directionalLight = new THREE.DirectionalLight(0xffffff, 2);
      directionalLight.position.set(0, 1, 2);
      scene.add(directionalLight);
    };

    const loadModel = (modelUrl = "/models/raccoon_head.glb") => {
      const loader = new GLTFLoader();
      loader.load(
        modelUrl,
        (gltf) => {
          if (modelRef.current) scene.remove(modelRef.current);
          const model = gltf.scene;
          model.scale.set(0.6, 0.6, 0.6);
          model.position.set(0, 0, 0.8);
          model.visible = true;
          scene.add(model);
          modelRef.current = model;
          setModelLoaded(true);
          console.log("✅ Model loaded:", modelUrl);
        },
        undefined,
        (error) => {
          console.error("❌ Failed to load model:", error);
        }
      );
    };

    const applyMatrixToModel = (matrixData) => {
      if (!matrixData?.length || !modelRef.current) return;

      const flat = matrixData.flat();
      const threeMatrix = new THREE.Matrix4();
      threeMatrix.set(...flat);

      const position = new THREE.Vector3();
      const quaternion = new THREE.Quaternion();
      const scale = new THREE.Vector3();
      threeMatrix.decompose(position, quaternion, scale);

      modelRef.current.position.copy(position);
      modelRef.current.quaternion.copy(quaternion);
      modelRef.current.scale.set(0.6, 0.6, 0.6);
      modelRef.current.position.y += 0.1;
      modelRef.current.position.z += 0.05;
    };

    const applyBlendshapes = (blendshapes) => {
      if (!modelRef.current || !blendshapes) return;

      modelRef.current.traverse((obj) => {
        if (obj.isMesh && obj.morphTargetDictionary && obj.morphTargetInfluences) {
          for (const [name, value] of Object.entries(blendshapes)) {
            const index = obj.morphTargetDictionary[name];
            if (index !== undefined) {
              obj.morphTargetInfluences[index] = value;
            }
          }
        }
      });
    };

    const connectWebSocket = () => {
      socket = new WebSocket("ws://localhost:8000/ws");

      socket.onopen = () => console.log("🟢 WebSocket connected");
      socket.onerror = (e) => console.error("🔴 WebSocket error:", e);
      socket.onclose = () => console.log("⚪️ WebSocket disconnected");

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setDebugData(data);

          const { matrix, blendshapes } = data;
          applyMatrixToModel(matrix);
          applyBlendshapes(blendshapes);
        } catch (err) {
          console.error("❌ WebSocket parse error:", err);
        }
      };
    };

    const connectMQTT = () => {
      client = mqtt.connect("ws://localhost:9001");

      client.on("connect", () => {
        console.log("📡 MQTT connected");
        client.subscribe("model/select");
      });

      client.on("message", (topic, message) => {
        if (topic === "model/select") {
          const modelUrl = message.toString(); // Assume full GLB URL (e.g. from S3)
          console.log("🔵 Loading new model:", modelUrl);
          loadModel(modelUrl);
        }
      });

      client.on("error", (err) => {
        console.error("❌ MQTT error:", err);
      });
    };

    const animate = () => {
      animationFrameId = requestAnimationFrame(animate);
      if (renderer && scene && camera) {
        renderer.render(scene, camera);
      }
    };

    const onWindowResize = () => {
      if (!camera || !renderer) return;
      camera.aspect = window.innerWidth / window.innerHeight;
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    };

    // --- Initialize ---
    initThree();
    loadModel(); // Load default raccoon_head.glb
    connectWebSocket();
    connectMQTT();
    animate();
    window.addEventListener("resize", onWindowResize);

    return () => {
      cancelAnimationFrame(animationFrameId);
      window.removeEventListener("resize", onWindowResize);
      if (socket) socket.close();
      if (client) client.end();
      if (renderer) renderer.dispose();
    };
  }, []);

  return (
    <div className="face-mask-container">
      <video ref={videoRef} className="video-background" autoPlay muted playsInline src="http://localhost:8000/video" />
      <div ref={containerRef} className="canvas-container" />
      <div className="debug-panel">
        <strong>🧠 Debug:</strong>
        <pre>{JSON.stringify(debugData, null, 2)}</pre>
        <p>{modelLoaded ? "✅ Model Loaded" : "⌛ Loading Model..."}</p>
      </div>
    </div>
  );
}