import React from "react";
import "../LP-css/top-bar.css";

const TopBar = ({ onNavigate, currentPage = 'home' }) => {
  const handleNavClick = (page) => {
    if (onNavigate) {
      onNavigate(page);
    }
  };

  return (
    <nav className="landing-navbar">
      <div className="landing-logo-section">
        <span className="landing-logo-icon">🎓</span>
        <h1 className="landing-logo-text">AcadScore</h1>
      </div>
      
      <div className="landing-nav-links">
        <a href="#" onClick={(e) => { e.preventDefault(); handleNavClick('home'); }} className={`landing-nav-link ${currentPage === 'home' ? 'active' : ''}`}>Home</a>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNavClick('about'); }} className={`landing-nav-link ${currentPage === 'about' ? 'active' : ''}`}>About</a>
        <a href="#" onClick={(e) => { e.preventDefault(); handleNavClick('contact'); }} className={`landing-nav-link ${currentPage === 'contact' ? 'active' : ''}`}>Contact</a>
      </div>
    </nav>
  );
};

export default TopBar;