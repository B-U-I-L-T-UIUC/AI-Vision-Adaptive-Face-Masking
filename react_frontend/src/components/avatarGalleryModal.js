import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/avatarGalleryModal.css"
import AddAvatar from "../components/addAvatar";
import avatar from "../components/avatarExample.png";

const avatars = Array(19).fill({ src: avatar }); /* fix later */

export default function AvatarGallery() {
  const navigate = useNavigate();

  return (
    <div className="avatar-gallery-container">
      <h1 className="gallery-title">AVAFM</h1>

      <div className="avatar-grid-container">
        <div className="avatar-grid">
          <div className="select-avatar-text">SELECT YOUR AVATAR</div>
          {/* fix routing here!!! */}
          <button className="exit-button" onClick={() => navigate("./pages/liveFeedPage")}>✖</button> 
          {avatars.map((avatar, index) => (
            <button key={index} className="avatar-btn">
              <img src={avatar.src} alt="avatar" className="avatar-image" />
            </button>
          ))}
          <AddAvatar />
        </div>
      </div>
    </div>
  );
}
