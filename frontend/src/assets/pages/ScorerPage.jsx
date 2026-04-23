import React, { useState, useEffect } from "react";
import "../css/ScorerPage.css";
import ConfirmationModal from "../Components/confirmationModal";

const ScorerPage = () => {
  const [essayPrompt, setEssayPrompt] = useState("");
  const [studentResponse, setStudentResponse] = useState("");
  const [dragActive, setDragActive] = useState(false);
  const [isModalOpen, setIsModalOpen] = useState(false);

  // ML Scoring state
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [scoringResult, setScoringResult] = useState(null);
  const [apiUrl] = useState("http://localhost:5000"); // Backend API URL

  // Rubrics state
  const [rubrics, setRubrics] = useState([]);
  const [selectedRubricId, setSelectedRubricId] = useState(1);
  const [loadingRubrics, setLoadingRubrics] = useState(true);

  // File Upload
  const fileInputRef = React.useRef(null);

  // Load available rubrics from backend on component mount
  useEffect(() => {
    const loadRubrics = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/rubrics`);
        if (response.ok) {
          const data = await response.json();
          setRubrics(data);
          if (data.length > 0) {
            setSelectedRubricId(data[0].id);
          }
        }
      } catch (err) {
        console.error("Error loading rubrics:", err);
      } finally {
        setLoadingRubrics(false);
      }
    };

    loadRubrics();
  }, [apiUrl]);

  const selectedRubric =
    rubrics.find((r) => r.id === selectedRubricId) || rubrics[0];

  const clearEssayPrompt = () => setEssayPrompt("");

  const clearAll = () => {
    setEssayPrompt("");
    setStudentResponse("");
    setScoringResult(null);
    setError(null);
  };

  // File Upload Handler
  const handleFileUpload = async (event) => {
    const file = event.target.files[0];
    if (!file) return;

    // UI/UX: Clear previous errors and show loading
    setIsLoading(true);
    setError(null);
    
    // Optional: Give the user feedback that the AI is working
    const originalPlaceholder = "AI is transcribing your photo...";
    setStudentResponse(originalPlaceholder);

    const formData = new FormData();
    formData.append("file", file);

    try {
      const response = await fetch(`${apiUrl}/api/ocr-extract`, {
        method: "POST",
        body: formData,
      });

      const data = await response.json();
      
      if (data.success) {
        setStudentResponse(data.extracted_text);
        console.log("✓ OCR Success!");
      } else {
        setStudentResponse(""); // Clear the placeholder
        setError(data.error || "OCR failed to recognize text.");
      }
    } catch (err) {
      setStudentResponse(""); 
      setError("Failed to connect to OCR service. Check your backend.");
    } finally {
      setIsLoading(false);
    }
  };

  // Score essay using ML backend
  const scoreEssay = async () => {
    if (!studentResponse.trim()) {
      setError("Please enter a student response");
      return;
    }

    if (studentResponse.trim().length < 10) {
      setError("Essay must be at least 10 characters long");
      return;
    }

    setIsLoading(true);
    setError(null);
    setScoringResult(null);

    try {
      const response = await fetch(`${apiUrl}/api/score`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          prompt: essayPrompt,
          response: studentResponse,
          rubric_id: selectedRubricId,
        }),
      });

      if (!response.ok) {
        throw new Error(`API error: ${response.status}`);
      }

      const data = await response.json();

      if (data.success) {
        setScoringResult(data);
        console.log("✓ Essay scored successfully:", data);
      } else {
        setError(data.error || "Failed to score essay");
      }
    } catch (err) {
      console.error("Error scoring essay:", err);
      setError(
        err.message.includes("Failed to fetch")
          ? "❌ Cannot connect to ML server. Make sure backend is running on port 5000."
          : `Error: ${err.message}`,
      );
    } finally {
      setIsLoading(false);
    }
  };

  const handleSaveRubrics = (updatedRubrics) => {
    console.log("Saved rubrics:", updatedRubrics);
  };

  return (
    <div className="main-notebook-container">
      <div className="inner-layout">
        {/* Left Panel - Student Essays */}
        <div className="left-panel">
          <div className="page-header">
            <h2>Student Essays</h2>
            <p>
              Manage essay questions and input student responses for grading.
            </p>
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

          {/* Updated Student Response Section */}
          <div className="input-section">
            <div className="section-label" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span>Student Response</span>
              <div className="ocr-buttons">
                <button 
                  type="button" 
                  className="ocr-btn" 
                  onClick={() => {
                    if (fileInputRef.current) {
                      fileInputRef.current.click();
                    } else {
                      console.error("File input ref is null");
                    }
                  }}
                  disabled={isLoading}
                >
                  📷 Upload File/Photo/PDF
                </button>
              </div>
            </div>
            
            <input 
              type="file" 
              ref={fileInputRef} 
              style={{display: 'none'}} 
              accept="image/*,.pdf" 
              onChange={handleFileUpload} 
            />
            
            <textarea
              className={`student-response-textarea ${dragActive ? "drag-active" : ""}`}
              placeholder="Enter student response here or drag & drop a file..."
              value={studentResponse}
              onChange={(e) => setStudentResponse(e.target.value)}
              onDragOver={(e) => { e.preventDefault(); setDragActive(true); }}
              onDragLeave={() => setDragActive(false)}
              onDrop={(e) => {
                e.preventDefault();
                setDragActive(false);
                const file = e.dataTransfer.files[0];
                if (!file) return;

                // UX Improvement: If they drop an image, trigger OCR automatically!
                if (file.type.startsWith("image/")) {
                  const fakeEvent = { target: { files: [file] } };
                  handleFileUpload(fakeEvent);
                } else if (file.type === "text/plain") {
                  const reader = new FileReader();
                  reader.onload = (event) => setStudentResponse(event.target.result);
                  reader.readAsText(file);
                }
              }}
            />
          </div>

            {/* Bottom Buttons */}
            <div className="button-group">
              <button
                className="clear-btn"
                onClick={clearAll}
                disabled={isLoading}
              >
                Clear
              </button>
              <button
                className="generate-btn"
                onClick={scoreEssay}
                disabled={isLoading || !studentResponse.trim()}
              >
                {isLoading ? "⏳ Scoring..." : "✨ Generate Score"}
              </button>
            </div>

            {/* Error Message */}
            {error && (
              <div className="error-message">
                <p>{error}</p>
              </div>
            )}
          </div>
        </div>

        {/* Right Panel - Rubric Evaluation */}
        <div className="right-panel">
          <div className="panel-header">
            <h3 className="panel-title">Rubric Evaluation</h3>
            <button className="edit-icon" onClick={() => setIsModalOpen(true)}>
              ✏️
            </button>
          </div>

          {/* Rubric Selector */}
          {!loadingRubrics && rubrics.length > 0 && (
            <div className="rubric-selector">
              <label htmlFor="rubric-select">Select Rubric:</label>
              <select
                id="rubric-select"
                value={selectedRubricId}
                onChange={(e) => setSelectedRubricId(Number(e.target.value))}
                disabled={isLoading}
              >
                {rubrics.map((rubric) => (
                  <option key={rubric.id} value={rubric.id}>
                    {rubric.title}
                  </option>
                ))}
              </select>
            </div>
          )}

          {!scoringResult ? (
            <div className="empty-state">
              <p>📝 Click "Generate Score" to see essay evaluation here</p>
              {selectedRubric && (
                <div className="rubric-preview">
                  <h4>📋 {selectedRubric.title} Rubric Criteria:</h4>
                  <ul>
                    {selectedRubric.criteria.map((criterion, idx) => (
                      <li key={idx}>
                        {criterion.name}:{" "}
                        <strong>{criterion.points} points</strong>
                      </li>
                    ))}
                  </ul>
                  <p className="total-points">
                    Total:{" "}
                    <strong>
                      {selectedRubric.criteria.reduce(
                        (sum, c) => sum + c.points,
                        0,
                      )}{" "}
                      points
                    </strong>
                  </p>
                </div>
              )}
            </div>
          ) : (
            <>
              {/* Rubric Cards with Scored Breakdown */}
              <div className="rubric-cards">
                {selectedRubric &&
                  selectedRubric.criteria.map((criterion, idx) => {
                    // Debug: log the entire scoring result
                    console.log('Full scoring result:', scoringResult);
                    console.log('Breakdown:', scoringResult.data?.breakdown);
                    console.log('Criterion name:', criterion.name);
                    
                    // Safe check for breakdown
                    if (!scoringResult.data?.breakdown) {
                      console.warn('No breakdown found in scoring result');
                      return null; // Skip this criterion
                    }
                    
                    // Try multiple possible key formats
                    const possibleKeys = [
                      criterion.name,
                      criterion.name.toLowerCase(),
                      criterion.name.toUpperCase(),
                      criterion.name.replace(/\s+/g, '_'),
                      criterion.name.replace(/\s+/g, '').toLowerCase()
                    ];
                    
                    let score = 0;
                    for (const key of possibleKeys) {
                      if (scoringResult.data.breakdown[key] !== undefined) {
                        score = scoringResult.data.breakdown[key];
                        break;
                      }
                    }
                    return (
                      <div className="rubric-card" key={idx}>
                        <h4>{criterion.name}</h4>
                        <div className="score-display">
                          <span className="score-value">{score}</span>
                          <span className="score-max">/{criterion.points}</span>
                        </div>
                        <div className="progress-bar">
                          <div
                            className="progress-fill"
                            style={{
                              width: `${(score / criterion.points) * 100}%`,
                            }}
                          />
                        </div>
                      </div>
                    );
                  })}
              </div>

              {/* Total Score Box */}
              <div className="total-score-box">
                <h4>Total Score</h4>
                <div className="total-score-display">
                  <span className="total-score-value">
                    {scoringResult.data?.total_score || 0}
                  </span>
                  <span className="total-score-max">/100</span>
                </div>
                <div className="confidence-meter">
                  <p className="confidence-label">
                    AI Confidence: {((scoringResult.data?.confidence || 0) * 100).toFixed(1)}
                    %
                  </p>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${(scoringResult.data?.confidence || 0) * 100}%` }}
                    />
                  </div>
                </div>
                <p className="overall-feedback">{scoringResult.data?.feedback || ''}</p>
              </div>
            </>
          )}
        </div>
      </div>

      {/* Rubric Edit Modal */}
      <ConfirmationModal
        isOpen={isModalOpen}
        onClose={() => setIsModalOpen(false)}
        onSave={handleSaveRubrics}
        selectedRubricId={selectedRubricId}
        apiUrl={apiUrl}
      />
    </div>
  );
};

export default ScorerPage;
