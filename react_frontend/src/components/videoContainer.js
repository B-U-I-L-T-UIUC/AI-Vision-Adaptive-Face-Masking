import { useEffect, useRef, useState } from "react";
import "../styles/videoContainer.css";
import LiveFeedNavigation from "../components/liveFeedNavigation";

export default function VideoContainer() {
  const videoRef = useRef(null);
  const [errorMessage, setErrorMessage] = useState("");

  useEffect(() => {
    let stream;
    async function startCamera() {
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
        const videoElement = videoRef.current;
        
        if (videoElement) {
          videoElement.srcObject = stream;
        }
      } catch (err) {
        console.error("Error accessing the camera:", err);
        setErrorMessage("Failed to access camera. Check browser settings.");
      }
    }

    startCamera();

    return () => {
      if (stream) {
        stream.getTracks().forEach(track => track.stop());
      }
    };
  }, []);

  return (
    <div className="parent">
      <div className="video-container">
        {/* rn its just regular video feed */}
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