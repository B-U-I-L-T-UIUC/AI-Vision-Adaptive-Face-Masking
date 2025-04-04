// import React from "react";
// import { useNavigate } from "react-router-dom";
// import "../styles/avatarGalleryModal.css"
// import AddAvatar from "../components/addAvatar";

// const avatars = Array(19).fill({ src: "/assets/avatarExample.png" });

// export default function AvatarGallery() {
//   const navigate = useNavigate();

//   return (
//     <div className="avatar-gallery-container">
//         <div className="avatar-grid-container">
//           <div className="select-avatar-text">SELECT YOUR AVATAR</div>
//           <button className="exit-button" onClick={() => navigate("../live-feed")}>✖</button> 
//           <div className="avatars">
//             {avatars.map((avatar, index) => (
//               <button key={index} className="avatar-btn">
//                 <img src={avatar.src} alt="avatar" className="avatar-image" />
//               </button>
//             ))}
//             <AddAvatar/>
//           </div>
//         </div>
//     </div>
//   );
// }


import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../styles/avatarGalleryModal.css";
import AddAvatar from "../components/addAvatar";

export default function AvatarGallery() {
  const navigate = useNavigate();
  const [avatars, setAvatars] = useState([]);
  
  // Fetch avatars from API on component mount
  useEffect(() => {
    const fetchAvatars = async () => {
      try {
        const response = await fetch("https://ko9kk91d64.execute-api.us-east-1.amazonaws.com/v1/mask");
        const data = await response.json();
        
        // Filter URLs that end with '.png'
        const pngAvatars = data.masksUrls.filter(url => url.endsWith('.png'));

        setAvatars(pngAvatars);
      } catch (error) {
        console.error("Error fetching avatars:", error);
      }
    };

    fetchAvatars();
  }, []);

  const handleImageClick = async (avatarUrl) => {
    // Extract the file name from the avatar URL
    const fileName = avatarUrl.substring(avatarUrl.lastIndexOf("/") + 1);
    const fileNameWithoutExtension = fileName.replace(".png", "");

    try {
      const response = await fetch("https://ko9kk91d64.execute-api.us-east-1.amazonaws.com/v1/feature/0", {
        method: "POST",
        headers: {
          // "Content-Type": "application/json",
        },
        body: JSON.stringify({
          feature: "mask",
          featureParam: fileNameWithoutExtension, // Send the file name
        }),
      });

      if (response.ok) {
        console.log("Image clicked and POST request sent successfully.");
      } else {
        console.error("Error sending POST request:", response.statusText);
      }
    } catch (error) {
      console.error("Error sending POST request:", error);
    }
  };

  
  return (
    <div className="avatar-gallery-container">
      <div className="avatar-grid-container">
        <div className="select-avatar-text">SELECT YOUR AVATAR</div>
        <button className="exit-button" onClick={() => navigate("../live-feed")}>✖</button> 
        <div className="avatars">
          {avatars.length > 0 ? (
            avatars.map((avatar, index) => (
              <button
                key={index}
                className="avatar-btn"
                onClick={() => handleImageClick(avatar)} // Attach the click handler
              >
                <img src={avatar} alt="avatar" className="avatar-image" />
              </button>
            ))
          ) : (
            <p>Loading avatars...</p> // Optionally show a loading message
          )}
          <AddAvatar/>
        </div>
      </div>
    </div>
  );
}
