import "../styles/addAvatar.css"

export default function AddAvatar() {
  const handleAddAvatar = () => {
    alert("upload avatar");
  };

  return (
    <button onClick={handleAddAvatar} className="add-avatar-btn">
        <img src="/assets/addicon.png" alt="gallery" className="add-avatar-icon" />
    </button>
  );
}
