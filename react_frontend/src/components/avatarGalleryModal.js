import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/avatarGalleryModal.css"
import AddAvatar from "../components/addAvatar";

const avatars = Array(19).fill({ src: "/assets/avatarExample.png" });

export default function AvatarGallery() {
  const navigate = useNavigate();

  return (
    <div className="avatar-gallery-container">
        <div className="avatar-grid-container">
          <div className="select-avatar-text">SELECT YOUR AVATAR</div>
          <button className="exit-button" onClick={() => navigate("../live-feed")}>✖</button> 
          <div className="avatars">
            {avatars.map((avatar, index) => (
              <button key={index} className="avatar-btn">
                <img src={avatar.src} alt="avatar" className="avatar-image" />
              </button>
            ))}
          <AddAvatar/>
          </div>
        </div>
    </div>
  );
}