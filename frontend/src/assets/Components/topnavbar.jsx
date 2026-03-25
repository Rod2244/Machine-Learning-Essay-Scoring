import React, { useState, useEffect } from 'react';
import '../css/topnavbar.css';

const Topnavbar = () => {
  const [showDropdown, setShowDropdown] = useState(false);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = () => setShowDropdown(false);
    document.addEventListener("click", handleClickOutside);
    return () => document.removeEventListener("click", handleClickOutside);
  }, []);

  return (
    <nav className="top-nav">
      <div className="logo-section">
        <span className="logo-icon">🎓</span>
        <h1 className="logo-text">AcadScore</h1>
      </div>

      <div className="user-section">
        <div
          className="profile-wrapper"
          onClick={(e) => {
            e.stopPropagation(); // prevent closing immediately
            setShowDropdown(!showDropdown);
          }}
        >
          <div className="profile-avatar">
            <svg width="22" height="22" viewBox="0 0 24 24" fill="none"
              stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
              <path d="M20 21v-2a4 4 0 0 0-4-4H8a4 4 0 0 0-4 4v2"/>
              <circle cx="12" cy="7" r="4"/>
            </svg>
          </div>

          <span className="profile-name">User</span>

          <svg
            className={`chevron ${showDropdown ? 'open' : ''}`}
            width="14"
            height="14"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2.5"
          >
            <polyline points="6 9 12 15 18 9"/>
          </svg>

          {showDropdown && (
            <div className="profile-dropdown">
              <div className="dropdown-item">
                <span>👤</span> My Profile
              </div>

              <div className="dropdown-item">
                <span>⚙️</span> Settings
              </div>

              <div className="dropdown-divider" />

              <div className="dropdown-item logout">
                <span>🚪</span> Log Out
              </div>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Topnavbar;