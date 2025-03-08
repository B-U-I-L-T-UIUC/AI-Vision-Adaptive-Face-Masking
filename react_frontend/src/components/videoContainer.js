import { useEffect, useRef, useState } from "react";
import "../styles/videoContainer.css";
import LiveFeedNavigation from "../components/liveFeedNavigation";

export default function VideoContainer() {
  const videoRef = useRef(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    async function startCamera() {
      try {
        const stream = await navigator.mediaDevices.getUserMedia({ video: true });
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing the camera:", err);
        setErrorMessage("Failed to access camera. Check browser settings.");
      }
    }

    startCamera();

    return () => {
      if (videoRef.current && videoRef.current.srcObject) {
        videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="parent">
      <div className="video-container">
        {/* only showing device camera feed for now */}
        {errorMessage ? (
          <div className="video-placeholder">{errorMessage}</div>
        ) : (
          <video ref={videoRef} autoPlay playsInline className="camera-feed"></video>
        )}
        <div className="live-feed-nav-wrapper">
          <LiveFeedNavigation />
        </div>
      </div>
    </div>
  );
}