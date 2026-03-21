import React from 'react';
import '../css/Sidebar.css';

const Sidebar = ({ activeTab, setActiveTab }) => {
  const tabs = [
    { name: 'Essays', icon: '📝' },
    { name: 'Rubrics', icon: '📋' },
    { name: 'History', icon: '🕒' }
  ];

  return (
    <div className="sidebar">
      {tabs.map((tab) => (
        <div 
          key={tab.name}
          className={`sidebar-item ${activeTab === tab.name ? 'active' : ''}`}
          onClick={() => setActiveTab(tab.name)}
        >
          <span className="icon">{tab.icon}</span>
          <span className="label">{tab.name}</span>
        </div>
      ))}
    </div>
  );
};

export default Sidebar;