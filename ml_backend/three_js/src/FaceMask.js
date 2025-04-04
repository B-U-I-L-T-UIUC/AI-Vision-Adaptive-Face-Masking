import React, { useEffect, useRef, useState } from "react";

const FaceMask = () => {
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const [faceLandmarker, setFaceLandmarker] = useState(null);
  const [webcamRunning, setWebcamRunning] = useState(false);
  const drawingUtilsRef = useRef(null); // Store DrawingUtils reference

  useEffect(() => {
    async function loadModel() {
      const vision = await import(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3"
      );
      const { FaceLandmarker, FilesetResolver, DrawingUtils } = vision;

      drawingUtilsRef.current = DrawingUtils; // Store DrawingUtils

      const filesetResolver = await FilesetResolver.forVisionTasks(
        "https://cdn.jsdelivr.net/npm/@mediapipe/tasks-vision@0.10.3/wasm"
      );

      const landmarker = await FaceLandmarker.createFromOptions(
        filesetResolver,
        {
          baseOptions: {
            modelAssetPath:
              "https://storage.googleapis.com/mediapipe-models/face_landmarker/face_landmarker/float16/1/face_landmarker.task",
            delegate: "GPU",
          },
          outputFaceBlendshapes: true,
          runningMode: "VIDEO",
          numFaces: 1,
        }
      );
      setFaceLandmarker(landmarker);
    }
    loadModel();
  }, []);

  const enableWebcam = async () => {
    if (!faceLandmarker) {
      console.log("Wait! faceLandmarker is not loaded yet.");
      return;
    }

    setWebcamRunning((prev) => !prev);

    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
      console.warn("getUserMedia() is not supported by your browser");
      return;
    }

    const stream = await navigator.mediaDevices.getUserMedia({ video: true });

    if (videoRef.current) {
      videoRef.current.srcObject = stream;
      videoRef.current.addEventListener("loadeddata", predictWebcam);
    }
  };

  const predictWebcam = async () => {
    if (!faceLandmarker || !videoRef.current || !canvasRef.current) return;

    const ctx = canvasRef.current.getContext("2d");
    if (!ctx) return;

    const drawingUtils = new drawingUtilsRef.current(ctx); // Use DrawingUtils correctly

    if (videoRef.current.readyState === 4) {
      canvasRef.current.width = videoRef.current.videoWidth;
      canvasRef.current.height = videoRef.current.videoHeight;

      // Debugging log for video dimensions
      console.log('Video Dimensions:', videoRef.current.videoWidth, videoRef.current.videoHeight);

      const results = await faceLandmarker.detectForVideo(
        videoRef.current,
        performance.now()
      );

      // Debugging log for face detection results
      console.log('Face Landmarks:', results.faceLandmarks);

      ctx.clearRect(0, 0, canvasRef.current.width, canvasRef.current.height);
      if (results.faceLandmarks && results.faceLandmarks.length > 0) {
        for (const landmarks of results.faceLandmarks) {
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_TESSELATION,
            { color: "#C0C0C070", lineWidth: 1 }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_RIGHT_EYE,
            { color: "#FF3030" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_RIGHT_EYEBROW,
            { color: "#FF3030" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_LEFT_EYE,
            { color: "#30FF30" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_LEFT_EYEBROW,
            { color: "#30FF30" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_FACE_OVAL,
            { color: "#E0E0E0" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_LIPS,
            { color: "#E0E0E0" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_RIGHT_IRIS,
            { color: "#FF3030" }
          );
          drawingUtils.drawConnectors(
            landmarks,
            faceLandmarker.FACE_LANDMARKS_LEFT_IRIS,
            { color: "#30FF30" }
          );
        }
      } else {
        console.log("No landmarks detected.");
      }
    }

    if (webcamRunning) {
      requestAnimationFrame(predictWebcam);
    }
  };

  return (
    <div>
      <h1>Face Landmarker in React</h1>
      <button onClick={enableWebcam}>
        {webcamRunning ? "Disable Webcam" : "Enable Webcam"}
      </button>
      <div style={{ position: "relative" }}>
        <video ref={videoRef} autoPlay playsInline style={{ width: "100%" }} />
        <canvas
          ref={canvasRef}
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            border: "1px solid red", // Add border to canvas for visibility
          }}
        />
      </div>
    </div>
  );
};

export default FaceMask;
