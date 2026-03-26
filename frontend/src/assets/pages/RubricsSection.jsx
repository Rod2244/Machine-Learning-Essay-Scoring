import React, { useState } from 'react';
import '../css/RubricsSection.css';
import RubricsEditsec from './RubricsEditsec';

const RubricsSection = () => {
  const [editing, setEditing] = useState(false);

  const handleSave = (data) => {
    console.log('Saved rubric:', data);
    setEditing(false);
  };

  if (editing) {
    return <RubricsEditsec onSave={handleSave} onCancel={() => setEditing(false)} />;
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <div className="header-flex">
          <h2>Rubrics</h2>
          <button className="edit-btn" onClick={() => setEditing(true)}>
            ✏️ Edit Rubric
          </button>
        </div>
        <p>Create and manage grading rubrics for essay evaluation</p>
      </div>

      <div className="rubrics-grid">
        <div className="rubric-item">
          <span className="rubric-icon">📝</span>
          <h3>Argumentative Essay</h3>
          <p>Evaluates thesis statement, evidence quality, logical reasoning, and counterarguments</p>
        </div>
        <div className="rubric-item">
          <span className="rubric-icon">📋</span>
          <h3>Expository Essay</h3>
          <p>Assesses clarity, organization, research integration, and explanatory power</p>
        </div>
        <div className="rubric-item">
          <span className="rubric-icon">📚</span>
          <h3>Narrative Essay</h3>
          <p>Measures storytelling elements, character development, and emotional engagement</p>
        </div>
        <div className="rubric-item">
          <span className="rubric-icon">🔬</span>
          <h3>Research Paper</h3>
          <p>Evaluates research depth, citation quality, analysis, and academic rigor</p>
        </div>
      </div>

      <div className="create-rubric-section">
        <h3>Create Custom Rubric</h3>
        <p>Design your own evaluation criteria with specific scoring guidelines</p>
        <button className="create-btn" onClick={() => setEditing(true)}>+ Create New Rubric</button>
      </div>
    </div>
  );
};

export default RubricsSection;