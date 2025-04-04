import { useEffect, useRef, useState } from "react";
import * as THREE from "three";
import { GLTFLoader } from "three/examples/jsm/loaders/GLTFLoader";
import "./FaceMask.css";

const FaceMask = () => {
  const containerRef = useRef(null);
  const raccoonRef = useRef(null);
  const glassesRef = useRef(null);
  const sceneRef = useRef(null);
  const [debugData, setDebugData] = useState({});
  const [selectedModel, setSelectedModel] = useState("raccoon");

  useEffect(() => {
    let renderer;
    let scene;
    let camera;
    let socket;

    const initThree = () => {
      // Initialize renderer only once
      if (!renderer) {
        renderer = new THREE.WebGLRenderer({ alpha: true });
        renderer.setSize(window.innerWidth, window.innerHeight);
        renderer.setClearColor(0x000000, 0);
        containerRef.current.appendChild(renderer.domElement);
      }

      // Initialize scene only once
      if (!scene) {
        scene = new THREE.Scene();
        sceneRef.current = scene;
      }

      // Initialize camera only once
      if (!camera) {
        camera = new THREE.PerspectiveCamera(80, window.innerWidth / window.innerHeight, 0.01, 100);
        camera.position.z = 2;
      }

      const light = new THREE.AmbientLight(0xffffff, 1.8);
      scene.add(light);
    };

    const loadModels = () => {
      const loader = new GLTFLoader();

      loader.load(
        "/models/raccoon_head.glb",
        (gltf) => {
          const raccoon = gltf.scene;
          raccoon.scale.set(3, 3, 3);
          raccoon.visible = false;
          sceneRef.current.add(raccoon);
          raccoonRef.current = raccoon;
        },
        undefined,
        (error) => console.error("Raccoon model load error:", error)
      );

      loader.load(
        "/models/glasses.glb",
        (gltf) => {
          const glasses = gltf.scene;
          glasses.scale.set(6, 6, 6);
          glasses.visible = false;
          sceneRef.current.add(glasses);
          glassesRef.current = glasses;
        },
        undefined,
        (error) => console.error("Glasses model load error:", error)
      );
    };

    const applyMatrixToModels = (matrixData) => {
      if (!matrixData?.length) return;

      const flat = matrixData.flat();
      const threeMatrix = new THREE.Matrix4();
      threeMatrix.set(...flat);

      const position = new THREE.Vector3();
      const quaternion = new THREE.Quaternion();
      const scale = new THREE.Vector3();
      threeMatrix.decompose(position, quaternion, scale);

      if (raccoonRef.current) {
        raccoonRef.current.position.copy(position);
        raccoonRef.current.quaternion.copy(quaternion);
        raccoonRef.current.scale.set(50, 50, 50);
        raccoonRef.current.position.y += 0.05;
        raccoonRef.current.position.z += 0.02;
      }

      if (glassesRef.current) {
        glassesRef.current.position.copy(position);
        glassesRef.current.quaternion.copy(quaternion);
        glassesRef.current.scale.set(120, 120, 10);
        glassesRef.current.position.y += 0.1;
        glassesRef.current.position.z += 0.03;
      }
    };

    const connectSocket = () => {
      socket = new WebSocket("ws://localhost:8000/ws");

      socket.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data);
          setDebugData(data);

          const { matrix, blendshapes } = data;
          applyMatrixToModels(matrix);

          [raccoonRef.current, glassesRef.current].forEach((model) => {
            if (model) {
              model.visible = model === getSelectedModel();
              model.traverse((obj) => {
                if (obj.isMesh && obj.morphTargetDictionary && obj.morphTargetInfluences) {
                  for (const [name, value] of Object.entries(blendshapes || {})) {
                    const index = obj.morphTargetDictionary[name];
                    if (index !== undefined) {
                      obj.morphTargetInfluences[index] = value;
                    }
                  }
                }
              });
            }
          });
        } catch (err) {
          console.error("WebSocket parse error:", err);
        }
      };

      socket.onopen = () => console.log("🟢 WS connected");
      socket.onerror = (e) => console.error("🔴 WS error", e);
      socket.onclose = () => console.log("⚪️ WS closed");
    };

    const getSelectedModel = () => {
      return selectedModel === "raccoon" ? raccoonRef.current : glassesRef.current;
    };

    const animate = () => {
      requestAnimationFrame(animate);
      if (sceneRef.current && camera) {
        renderer.render(sceneRef.current, camera);
      }
    };

    const setup = () => {
      initThree();
      loadModels();
      connectSocket();
      animate();
    };

    setup();
    return () => {
      if (socket) socket.close();
    };
  }, [selectedModel]);

  return (
    <>
          {/* Video Feed */}
          <img className="video-background" src="http://localhost:8000/video" alt="Video Feed" />
      <div ref={containerRef} className="canvas-container" />


      {/* Controls */}
      <div
        className="dropzone"
        onDragOver={(e) => e.preventDefault()}
        onDrop={(e) => {
          const model = e.dataTransfer.getData("model");
          if (model) {
            setSelectedModel(model);
          }
        }}
      >
        Drop here to change model
      </div>

      {/* Debug info */}
      <div className="debug-panel">
        <strong>🧠 Debug:</strong>
        <pre>{JSON.stringify(debugData, null, 2)}</pre>
      </div>
    </>
  );
};

export default FaceMask;
