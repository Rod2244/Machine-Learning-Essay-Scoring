import React from 'react';
import '../css/HistoryPage.css';

const HistoryPage = () => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Essay History</h2>
        <p>View and analyze previously graded essays and their evaluation results</p>
      </div>

      <div className="empty-state">
        <div className="empty-icon">📚</div>
        <h3>No Essay History Yet</h3>
        <p>Start grading essays to see your evaluation history and analytics here.</p>
      </div>
    </div>
  );
};

export default HistoryPage;