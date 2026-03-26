import React, { useState, useRef, useEffect } from 'react';
import '../css/topnavbar.css';

const Topnavbar = ({ user, onLogout }) => {
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const dropdownRef = useRef(null);

  // Close dropdown when clicking outside
  useEffect(() => {
    const handleClickOutside = (e) => {
      if (dropdownRef.current && !dropdownRef.current.contains(e.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  // Get initials from user name
  const getInitials = (name) => {
    if (!name) return '?';
    return name.split(' ').map(n => n[0]).join('').toUpperCase().slice(0, 2);
  };

  return (
    <nav className="top-nav">
      <div className="logo-section">
        <span className="logo-icon">🎓</span>
        <h1 className="logo-text">AcadScore</h1>
      </div>

      <div className="user-section">
        <button className="settings-btn" title="Settings">⚙️</button>

        {/* User Avatar + Dropdown */}
        <div className="profile-dropdown-wrapper" ref={dropdownRef}>
          <button
            className="avatar-btn"
            onClick={() => setDropdownOpen(prev => !prev)}
            title={user?.name || 'Account'}
            aria-expanded={dropdownOpen}
          >
            <div className="avatar-circle">
              {getInitials(user?.name)}
            </div>
          </button>

          {dropdownOpen && (
            <div className="profile-dropdown">
              <div className="dropdown-user-info">
                <div className="dropdown-avatar">
                  {getInitials(user?.name)}
                </div>
                <div className="dropdown-details">
                  <span className="dropdown-name">{user?.name || 'User'}</span>
                  <span className="dropdown-email">{user?.email || ''}</span>
                </div>
              </div>
              <div className="dropdown-divider" />
              <button
                className="dropdown-item logout-item"
                onClick={() => {
                  setDropdownOpen(false);
                  onLogout();
                }}
              >
                <span className="dropdown-item-icon">🚪</span>
                Log Out
              </button>
            </div>
          )}
        </div>
      </div>
    </nav>
  );
};

export default Topnavbar;