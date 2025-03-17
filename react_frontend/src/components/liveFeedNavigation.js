import React from "react";
import { useNavigate } from "react-router-dom";
import "../styles/liveFeedNavigation.css"
export default function LiveFeedNavigation() {
    const navigate = useNavigate();
    return (
        <>
        <div className="buttons">
            <img src="/assets/arrow.png" alt="right-arrow" className="left_img"/>
            <img src="/assets/galleryicon.png" alt="gallery" className="gallery_button" onClick={() => navigate("../avatar-gallery")}/>
            <img src="/assets/arrow.png" alt="right-arrow" className="right_img"/>
        </div>
        </>
    );
}