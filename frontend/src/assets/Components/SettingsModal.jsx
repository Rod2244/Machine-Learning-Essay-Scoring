import React, { useState, useEffect } from 'react';
import '../css/SettingsModal.css';

const SettingsModal = ({ isOpen, onClose, isDarkMode, onToggleDarkMode }) => {
  const [settings, setSettings] = useState({
    darkMode: isDarkMode,
  });

  useEffect(() => {
    setSettings(prev => ({
      ...prev,
      darkMode: isDarkMode
    }));
  }, [isDarkMode]);

  const handleDarkModeToggle = () => {
    setSettings(prev => ({
      ...prev,
      darkMode: !prev.darkMode
    }));
    onToggleDarkMode();
  };

  if (!isOpen) return null;

  return (
    <>
      {/* Backdrop */}
      <div className="settings-backdrop" onClick={onClose} />

      {/* Modal */}
      <div className="settings-modal">
        {/* Header */}
        <div className="settings-header">
          <h2 className="settings-title">Settings</h2>
          <button
            className="settings-close-btn"
            onClick={onClose}
            aria-label="Close settings"
          >
            ✕
          </button>
        </div>

        {/* Divider */}
        <div className="settings-divider" />

        {/* Settings Content */}
        <div className="settings-content">
          {/* Display Section */}
          <div className="settings-section">
            <h3 className="section-title">Display</h3>

            {/* Dark Mode Toggle */}
            <div className="settings-item">
              <div className="setting-info">
                <span className="setting-icon">🌙</span>
                <div className="setting-details">
                  <span className="setting-name">Dark Mode</span>
                  <span className="setting-description">
                    Easier on the eyes during night studying
                  </span>
                </div>
              </div>
              <label className="toggle-switch">
                <input
                  type="checkbox"
                  checked={settings.darkMode}
                  onChange={handleDarkModeToggle}
                />
                <span className="toggle-slider" />
              </label>
            </div>
          </div>

          {/* About Section */}
          <div className="settings-section">
            <h3 className="section-title">About</h3>
            <div className="about-item">
              <span className="about-label">Version:</span>
              <span className="about-value">1.0.0</span>
            </div>
            <div className="about-item">
              <span className="about-label">Build:</span>
              <span className="about-value">2026.05.04</span>
            </div>
          </div>
        </div>

        {/* Footer */}
        <div className="settings-footer">
          <button className="settings-close-action-btn" onClick={onClose}>
            Done
          </button>
        </div>
      </div>
    </>
  );
};

export default SettingsModal;
