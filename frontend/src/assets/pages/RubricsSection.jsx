import React from 'react';
import '../css/RubricsSection.css';

const RubricsSection = () => {
  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Rubrics</h2>
        <p>Create and manage grading rubrics for essay evaluation</p>
      </div>

      <div className="rubrics-grid">
        <div className="rubric-item">
          <div className="rubric-icon">📝</div>
          <h3>Argumentative Essay</h3>
          <p>Evaluates thesis statement, evidence quality, logical reasoning, and counterarguments</p>
        </div>
        
        <div className="rubric-item">
          <div className="rubric-icon">📋</div>
          <h3>Expository Essay</h3>
          <p>Assesses clarity, organization, research integration, and explanatory power</p>
        </div>
        
        <div className="rubric-item">
          <div className="rubric-icon">📚</div>
          <h3>Narrative Essay</h3>
          <p>Measures storytelling elements, character development, and emotional engagement</p>
        </div>
        
        <div className="rubric-item">
          <div className="rubric-icon">🔬</div>
          <h3>Research Paper</h3>
          <p>Evaluates research depth, citation quality, analysis, and academic rigor</p>
        </div>
      </div>

      <div className="create-rubric-section">
        <h3>Create Custom Rubric</h3>
        <p>Design your own evaluation criteria with specific scoring guidelines</p>
        <button className="create-btn">+ Create New Rubric</button>
      </div>
    </div>
  );
};

export default RubricsSection;