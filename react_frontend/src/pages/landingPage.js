import { useNavigate } from 'react-router-dom'; // Importing useNavigate hook
import '../styles/landingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();
  
  const handleStartClick = () => {
    navigate('/avatar-gallery'); 
  };

  return (
    <>
      <div className="k">
        <header className="header">
          <img className="built-logo" src={`${process.env.PUBLIC_URL}/assets/built.png`} alt="built logo" />
          <div className="titlenbutton">
          <h1 className="title">AI Vision: Adaptive Face Masking
          </h1>
          <button onClick={handleStartClick}>Click to Start!</button>
          </div>
        </header>



        {/* Footer with the credit */}
      <footer>
        <p>
          Credit to <a href="https://built-illinois.org/#/Home" target="_blank" rel="noopener noreferrer">B[U]ILT's Tech Committee</a>
        </p>
      </footer>

    </div>
    </>
  );
}