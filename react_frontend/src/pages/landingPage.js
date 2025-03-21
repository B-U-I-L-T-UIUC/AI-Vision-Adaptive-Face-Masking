import { useNavigate } from 'react-router-dom'; // Importing useNavigate hook
import './landingPage.css';

export default function LandingPage() {
  const navigate = useNavigate();
  
  const handleStartClick = () => {
    navigate('/live-feed'); 
  };

  return (
    <>
      <div className="k">
        <header className="header">
          <img className="built-logo" src={`${process.env.PUBLIC_URL}/assets/built.png`} alt="built logo" />
          <h1 className="title">AVAFM</h1>
        </header>

        <section id="main">
          <button onClick={handleStartClick}>Click to Start</button>
        </section>

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