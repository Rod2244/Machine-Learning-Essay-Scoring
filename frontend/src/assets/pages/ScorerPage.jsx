import React, { useState } from 'react';
import '../css/ScorerPage.css';

const ScorerPage = () => {
  const [essayPrompt, setEssayPrompt] = useState('');

  // 
  const [studentResponse, setStudentResponse] = useState('');
  const [dragActive, setDragActive] = useState(false);

  return (
    <div className="main-notebook-container">
      <div className="inner-layout">
        {/* Left Panel - Student Essays */}
        <div className="left-panel">
          <div className="page-header">
            <h2>Student Essays</h2>
            <p>Manage essay questions and input student responses for grading.</p>
          </div>
          
          <div className="essay-sections">
            {/* Essay Prompt Section */}
            <div className="input-section">
              <div className="section-label">Essay Prompt</div>
              <div className="input-row">
                <div className="input-wrapper">
                  <input 
                    type="text" 
                    className="essay-prompt-input"
                    placeholder="Enter the essay question here..."
                    value={essayPrompt}
                    onChange={(e) => setEssayPrompt(e.target.value)}
                  />
                  {essayPrompt && (
                    <button 
                      className="clear-input-btn"
                      onClick={clearEssayPrompt}
                      title="Clear essay prompt"
                    >
                      ✕
                    </button>
                  )}
                </div>
                <button className="save-btn">Save</button>
              </div>
            </div>
            
            {/* Student Response Section */}
              <div className="input-section">
              <div className="section-label">Student Response</div>
                <textarea className={`student-response-textarea ${dragActive ? "drag-active" : ""}`}
                placeholder="Enter student response here or drag & drop a file..."
                value={studentResponse}
                onChange={(e) => setStudentResponse(e.target.value)}
                onDragOver={(e) => {
                  e.preventDefault();
                setDragActive(true);
         }}

          onDragLeave={() => setDragActive(false)}

          onDrop={(e) => {
            e.preventDefault();
            setDragActive(false);

            const file = e.dataTransfer.files[0];
            if (!file) return;

            // ✅ TXT = auto read content
            if (file.type === "text/plain") {
              const reader = new FileReader();
              reader.onload = (event) => {
                setStudentResponse(event.target.result);
              };
              reader.readAsText(file);
            } else {
              // ✅ other files = show filename
              setStudentResponse(`[Attached File]: ${file.name}`);
            }
          }}
        />
        </div>
            
            {/* Bottom Buttons */}
            <div className="button-group">
              <button className="clear-btn">Clear</button>
              <button className="generate-btn">Generate</button>
            </div>
          </div>
        </div>
        
        {/* Right Panel - Rubric Evaluation */}
        <div className="right-panel">
          <div className="panel-header">
            <h3 className="panel-title">Rubric Evaluation</h3>
            <button className="edit-icon">✏️</button>
          </div>
          
          <div className="rubric-cards">
            {/* Grammar & Mechanics Card */}
            <div className="rubric-card">
              <h4>Grammar & Mechanics</h4>
              <div className="score-display">
                <span className="score-value">85</span>
                <span className="score-max">/100</span>
              </div>
              <p className="rubric-feedback">
                Strong command of grammar and mechanics. Minor punctuation errors present.
              </p>
            </div>
            
            {/* Structure & Organization Card */}
            <div className="rubric-card">
              <h4>Structure & Organization</h4>
              <div className="score-display">
                <span className="score-value">78</span>
                <span className="score-max">/100</span>
              </div>
              <p className="rubric-feedback">
                Clear structure with logical flow. Introduction and conclusion are well-developed.
              </p>
            </div>
            
            {/* Clarity & Style Card */}
            <div className="rubric-card">
              <h4>Clarity & Style</h4>
              <div className="score-display">
                <span className="score-value">92</span>
                <span className="score-max">/100</span>
              </div>
              <p className="rubric-feedback">
                Writing is clear and engaging. Good use of vocabulary and sentence variety.
              </p>
            </div>
          </div>
          
          {/* Total Score Box */}
          <div className="total-score-box">
            <h4>Total Score</h4>
            <div className="total-score-display">
              <span className="total-score-value">85</span>
              <span className="total-score-max">/100</span>
            </div>
            <p className="overall-feedback">
              Overall performance demonstrates strong writing skills with room for improvement in organization.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ScorerPage;