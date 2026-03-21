import React from 'react';
import '../css/topnavbar.css';

const Topnavbar = () => {
  return (
    <nav className="top-nav">
      <div className="logo-section">
        <span className="logo-icon">🎓</span>
        <h1 className="logo-text">AcadScore</h1>
      </div>
      <div className="user-section">
        <img src="https://via.placeholder.com/40" alt="Profile" className="profile-img" />
        <button className="settings-btn">⚙️</button>
      </div>
    </nav>
  );
};

export default Topnavbar;