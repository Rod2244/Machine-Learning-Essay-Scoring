import React, { useState } from 'react';
import Topnavbar from './assets/Components/topnavbar';
import ScorerPage from './assets/pages/ScorerPage';
import RubricsSection from './assets/pages/RubricsSection';
import HistoryPage from './assets/pages/HistoryPage';
import './index.css';

const App = () => {
  const [activeTab, setActiveTab] = useState('essays');

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
      <Topnavbar />
      <div className="main-layout">
        {/* Notebook Tabs Container */}
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
        
        {/* Outer Frame - Grey Container */}
        <div className="outer-frame">
          {/* Inner Workspace - White Container */}
          <div className="inner-workspace">
            {renderPage()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;