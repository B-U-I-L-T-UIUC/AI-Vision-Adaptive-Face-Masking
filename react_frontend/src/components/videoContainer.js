import "../styles/videoContainer.css";
import LiveFeedNavigation from "./liveFeedNavigation";
import FaceMask from "./FaceMask";

export default function VideoContainer() {
  return (
    <div className="parent">
      <div className="video-container">
        {/* ✅ Corrected className */}
        <img
          src="http://localhost:8000/video"
          alt="Live feed"
          className="camera-feed"
        />
        
        <FaceMask />
        
        <div className="live-feed-nav-wrapper">
          <LiveFeedNavigation />
        </div>
      </div>
    </div>
  );
}