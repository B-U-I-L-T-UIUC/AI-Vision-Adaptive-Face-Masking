import './App.css';
import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import LandingPage from "./pages/landingPage";
import LiveFeedPage from "./pages/liveFeedPage";
import AvatarGallery from "./pages/avatarGallery";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/live-feed" element={<LiveFeedPage />} />
        <Route path="/avatar-gallery" element={<AvatarGallery />} />
      </Routes>
    </Router>
  );
}