import React, { useEffect } from "react";
import { useNavigate } from "react-router-dom";
import "../LP-css/home.css";
import TopBar from "../LP-components/top-bar";
import homeBgImage from "../../homepage.png.png";
import guyImage from "../../Guy.png";
import questionIcon from "../../question.png";
import criteriaIcon from "../../criteria.png";
import writeessayIcon from "../../writeessay.png";
import resultsIcon from "../../results.png";

export default function Home({ onNavigate }) {
  const navigate = useNavigate();

  // Force light mode on landing page
  useEffect(() => {
    // Remove dark-mode class if it exists
    document.documentElement.classList.remove('dark-mode');
  }, []);

  const handleTryNow = () => {
    navigate('/login');
  };

  return (
    <div className="home">
      <TopBar onNavigate={onNavigate} currentPage="home" />

      {/* HERO SECTION */}
      <section className="hero" id="home">
        <div className="hero-overlay" />

        <div className="hero-content">
          <h1 className="delight-title">Essay Scoring System</h1>
          <p>
            Easily evaluate essays based on your own criteria. 
            Input a question, write an essay, and get a score instantly.
          </p>
          <button className="primary-btn" onClick={handleTryNow}>Try Now</button>
        </div>
        
        {/* DECORATIVE IMAGE */}
        <div className="hero-decoration">
          <img src={homeBgImage} alt="Decorative element" className="hero-bg-image" />
        </div>

        {/* GUY IMAGE */}
        <div className="guy-container">
          <img src={guyImage} alt="Person" className="guy-image" />
        </div>
      </section>

      {/* INTRO */}
      <section className="section light">
        <div className="container center">
          <h2>Why Choose us?</h2>
          <p>
            This website helps users check and evaluate essays quickly and efficiently.
            Set your own criteria and receive accurate scoring based on your standards.
          </p>
        </div>
      </section>

      {/* HOW TO USE */}
      <section className="section">
        <div className="container">
          <h2 className="left-align">How It Works</h2>

          <div className="how-it-works-timeline">
            <div className="timeline-step">
              <div className="step-icon">
                <span className="step-number">1</span>
                <img src={questionIcon} alt="Question" className="step-icon-image" />
              </div>
              <div className="step-content">
                <h3>Enter a Question</h3>
                <p>Type your essay prompt.</p>
              </div>
            </div>

            <div className="timeline-step">
              <div className="step-icon">
                <span className="step-number">2</span>
                <img src={criteriaIcon} alt="Criteria" className="step-icon-image" />
              </div>
              <div className="step-content">
                <h3>Set Criteria</h3>
                <p>Define how it will be graded.</p>
              </div>
            </div>

            <div className="timeline-step">
              <div className="step-icon">
                <span className="step-number">3</span>
                <img src={writeessayIcon} alt="Write Essay" className="step-icon-image" />
              </div>
              <div className="step-content">
                <h3>Write Essay</h3>
                <p>Paste or type your essay.</p>
              </div>
            </div>

            <div className="timeline-step">
              <div className="step-icon">
                <span className="step-number">4</span>
                <img src={resultsIcon} alt="Results" className="step-icon-image" />
              </div>
              <div className="step-content">
                <h3>Get Results</h3>
                <p>Instant scoring and feedback.</p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* FEATURES */}
      <section className="section light">
        <div className="container center">
          <h2>Features</h2>

          <div className="features">
            <div>
              <strong>Instant Essay Checking</strong><br />
              Quickly evaluate essays and receive results in just a few seconds.
            </div>

            <div>
              <strong>Custom Scoring Criteria</strong><br />
              Define your own standards such as grammar, content, and organization.
            </div>

            <div>
              <strong>Consistent Evaluation</strong><br />
              Ensures fair and uniform scoring based on selected criteria.
            </div>

            <div>
              <strong>User-Friendly Interface</strong><br />
              Simple and easy-to-use design for a smooth user experience.
            </div>
          </div>
        </div>
      </section>

      {/* FOOTER */}
      <footer className="footer">
        <div className="container">
          <p className="credit"> 2026 Essay Scoring System. All rights reserved.</p>
          <p className="attribution">Images and design elements: CTTO </p>
        </div>
      </footer>
    </div>
  );
}