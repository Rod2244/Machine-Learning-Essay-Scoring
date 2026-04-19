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

            {/* Student Response Section */}
            <div className="input-section">
              <div className="section-label">Student Response</div>
              <textarea
                className={`student-response-textarea ${dragActive ? "drag-active" : ""}`}
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

                  if (file.type === "text/plain") {
                    const reader = new FileReader();
                    reader.onload = (event) => {
                      setStudentResponse(event.target.result);
                    };
                    reader.readAsText(file);
                  } else {
                    setStudentResponse(`[Attached File]: ${file.name}`);
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
                    const score =
                      scoringResult.breakdown[criterion.name.toLowerCase()] ||
                      0;
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
                    {scoringResult.score}
                  </span>
                  <span className="total-score-max">/100</span>
                </div>
                <div className="confidence-meter">
                  <p className="confidence-label">
                    AI Confidence: {(scoringResult.confidence * 100).toFixed(1)}
                    %
                  </p>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{ width: `${scoringResult.confidence * 100}%` }}
                    />
                  </div>
                </div>
                <p className="overall-feedback">{scoringResult.feedback}</p>
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
