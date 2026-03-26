import React, { useState } from 'react';
import Topnavbar from './assets/Components/topnavbar';
import ScorerPage from './assets/pages/ScorerPage';
import RubricsSection from './assets/pages/RubricsSection';
import HistoryPage from './assets/pages/HistoryPage';
import LoginPage from './assets/pages/LoginPage';
import './index.css';

const App = () => {
  const [user, setUser] = useState(null); // null = not logged in
  const [activeTab, setActiveTab] = useState('essays');

  const handleLogin = (userData) => {
    setUser(userData);
  };

  const handleLogout = () => {
    setUser(null);
    setActiveTab('essays');
  };

  // Show login page if not logged in
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (activeTab) {
      case 'essays':
        return <ScorerPage />;
      case 'rubrics':
        return <RubricsSection />;
      case 'history':
        return <HistoryPage />;
      default:
        return <ScorerPage />;
    }
  };

  return (
    <div className="app-container">
      <Topnavbar user={user} onLogout={handleLogout} />
      <div className="main-layout">
        {/* Notebook Tabs */}
        <div className="notebook-tabs-container">
          <div
            className={`notebook-tab ${activeTab === 'essays' ? 'active' : ''}`}
            onClick={() => setActiveTab('essays')}
          >
            <span className="icon">📝</span>
            <span className="label">Essays</span>
          </div>
          <div
            className={`notebook-tab ${activeTab === 'rubrics' ? 'active' : ''}`}
            onClick={() => setActiveTab('rubrics')}
          >
            <span className="icon">📋</span>
            <span className="label">Rubrics</span>
          </div>
          <div
            className={`notebook-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <span className="icon">📚</span>
            <span className="label">History</span>
          </div>
        </div>

        {/* Outer Frame */}
        <div className="outer-frame">
          <div className="inner-workspace">
            {renderPage()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;