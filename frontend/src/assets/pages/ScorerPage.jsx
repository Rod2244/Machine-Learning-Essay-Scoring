import React, { useState, useEffect } from "react";
import "../css/ScorerPage.css";
import ConfirmationModal from "../Components/confirmationModal";

const ScorerPage = () => {
  const [essayPrompt, setEssayPrompt] = useState("");
  const [studentName, setStudentName] = useState("");
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

  // ✅ Load saved essay prompt from localStorage on mount
  useEffect(() => {
    const savedPrompt = localStorage.getItem("savedEssayPrompt");
    if (savedPrompt) {
      setEssayPrompt(savedPrompt);
      console.log("✓ Loaded saved essay prompt from storage");
    }
    
    console.log("📖 ScorerPage mounted - checking localStorage:");
    console.log("   user_id:", localStorage.getItem("user_id"));
    console.log("   user_full_name:", localStorage.getItem("user_full_name"));
    console.log(
      "   session_token exists:",
      !!localStorage.getItem("session_token"),
    );
    console.log("   All localStorage keys:", Object.keys(localStorage));
  }, []);

  // Load available rubrics from backend on component mount
  useEffect(() => {
    const loadRubrics = async () => {
      try {
        const response = await fetch(`${apiUrl}/api/rubrics`);
        if (response.ok) {
          const data = await response.json();
          setRubrics(data);
          if (data.length > 0) {
            const firstId = data[0].id;
            // keep numeric ids as numbers, UUIDs as strings
            const parsedId = /^\d+$/.test(String(firstId))
              ? Number(firstId)
              : String(firstId);
            setSelectedRubricId(parsedId);
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
    rubrics.find(
      (r) =>
        r.id === selectedRubricId || String(r.id) === String(selectedRubricId),
    ) || rubrics[0];

  // Function to get progress status and color
  const getProgressStatus = (percentage) => {
    if (percentage >= 76) {
      return {
        status: "Excellent",
        color: "#27ae60",
        backgroundColor: "rgba(39, 174, 96, 0.1)",
      };
    } else if (percentage >= 51) {
      return {
        status: "Proficient",
        color: "#2980b9",
        backgroundColor: "rgba(41, 128, 185, 0.1)",
      };
    } else if (percentage >= 26) {
      return {
        status: "Developing",
        color: "#f39c12",
        backgroundColor: "rgba(243, 156, 18, 0.1)",
      };
    } else {
      return {
        status: "Beginning",
        color: "#e74c3c",
        backgroundColor: "rgba(231, 76, 60, 0.1)",
      };
    }
  };

  const clearEssayPrompt = () => setEssayPrompt("");

  // Save essay prompt to localStorage
  const handleSavePrompt = () => {
    if (essayPrompt.trim()) {
      localStorage.setItem("savedEssayPrompt", essayPrompt);
      console.log("✓ Essay prompt saved successfully");
      // Optional: Show brief success feedback
      alert("Essay prompt saved! ✓");
    } else {
      alert("Cannot save an empty essay prompt");
    }
  };

  const clearAll = () => {
    setEssayPrompt("");
    setStudentName("");
    setStudentResponse("");
    setScoringResult(null);
    setError(null);
    localStorage.removeItem("savedEssayPrompt"); // Also clear saved prompt
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
      // Get user_id from localStorage (set during login)
      const user_id = localStorage.getItem("user_id");
      const user_full_name = localStorage.getItem("user_full_name");
      const session_token = localStorage.getItem("session_token");

      console.log("📝 Scoring essay...");
      console.log("   user_id:", user_id);
      console.log("   user_full_name:", user_full_name);
      console.log("   session_token exists:", !!session_token);
      console.log("   localStorage keys:", Object.keys(localStorage));

      // Validate user_id exists and is a valid UUID
      if (
        !user_id ||
        user_id === "null" ||
        user_id === "undefined" ||
        user_id.length === 0
      ) {
        console.error("❌ ERROR: user_id is missing or invalid!");
        console.error("   localStorage user_id:", user_id);
        console.error("   localStorage contents:", {
          user_id: localStorage.getItem("user_id"),
          user_full_name: localStorage.getItem("user_full_name"),
          session_token: localStorage.getItem("session_token"),
        });
        setError(
          "❌ Session expired. Please log in again to save your essay scores.",
        );
        setIsLoading(false);
        return;
      }

      const requestBody = {
        prompt: essayPrompt,
        response: studentResponse,
        rubric_id: selectedRubricId,
        user_id: user_id, // ✓ Include user_id
        student_name: studentName || user_full_name || "Student",
        essay_type: selectedRubric?.title || "Essay",
      };

      console.log("📤 Sending request to backend:", requestBody);
      console.log("📤 Selected Rubric Details:", {
        id: selectedRubric?.id,
        title: selectedRubric?.title,
        isCustom: selectedRubric?.isCustom,
        criteriaCount: selectedRubric?.criteria?.length,
        rubric_id_being_sent: selectedRubricId,
      });

      const response = await fetch(`${apiUrl}/api/score`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(requestBody),
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
                    value={essayPrompt} onClick={handleSavePrompt}
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

            {/* Student Name Section */}
            <div className="input-section">
              <div className="section-label">Student Name <span style={{fontSize: '0.85em', color: '#999'}}>(Optional)</span></div>
              <div className="input-row">
                <div className="input-wrapper">
                  <input
                    type="text"
                    className="essay-prompt-input"
                    placeholder="Leave blank to use your account name"
                    value={studentName}
                    onChange={(e) => setStudentName(e.target.value)}
                  />
                  {studentName && (
                    <button
                      className="clear-input-btn"
                      onClick={() => setStudentName("")}
                      title="Clear student name"
                    >
                      ✕
                    </button>
                  )}
                </div>
              </div>
            </div>

            {/* Updated Student Response Section */}
            <div className="input-section">
              <div
                className="section-label"
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
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
                style={{ display: "none" }}
                accept="image/*,.pdf"
                onChange={handleFileUpload}
              />

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

                  // UX Improvement: If they drop an image, trigger OCR automatically!
                  if (file.type.startsWith("image/")) {
                    const fakeEvent = { target: { files: [file] } };
                    handleFileUpload(fakeEvent);
                  } else if (file.type === "text/plain") {
                    const reader = new FileReader();
                    reader.onload = (event) =>
                      setStudentResponse(event.target.result);
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
                value={String(selectedRubricId)}
                onChange={(e) => {
                  const val = e.target.value;
                  const parsed = /^\d+$/.test(val) ? Number(val) : val;
                  setSelectedRubricId(parsed);
                }}
                disabled={isLoading}
              >
                {rubrics.map((rubric) => (
                  <option key={rubric.id} value={String(rubric.id)}>
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
                    console.log("Full scoring result:", scoringResult);
                    console.log("Breakdown:", scoringResult?.breakdown);
                    console.log("Criterion name:", criterion.name);

                    // Safe check for breakdown - access directly from scoringResult
                    if (!scoringResult?.breakdown) {
                      console.warn("No breakdown found in scoring result");
                      return null; // Skip this criterion
                    }

                    // Try multiple possible key formats
                    const possibleKeys = [
                      criterion.name,
                      criterion.name.toLowerCase(),
                      criterion.name.toUpperCase(),
                      criterion.name.replace(/\s+/g, "_"),
                      criterion.name.replace(/\s+/g, "").toLowerCase(),
                    ];

                    let score = 0;
                    for (const key of possibleKeys) {
                      if (scoringResult.breakdown[key] !== undefined) {
                        score = scoringResult.breakdown[key];
                        console.log(
                          `✓ Found score for ${criterion.name}: ${score}`,
                        );
                        break;
                      }
                    }

                    if (score === 0) {
                      console.warn(
                        `⚠️ No score found for ${criterion.name} in breakdown:`,
                        scoringResult.breakdown,
                      );
                    }

                    const percentage = (score / criterion.points) * 100;
                    const progressStatus = getProgressStatus(percentage);

                    return (
                      <div className="rubric-card" key={idx}>
                        <h4>{criterion.name}</h4>
                        <div className="score-display">
                          <span className="score-value">{score}</span>
                          <span className="score-max">/{criterion.points}</span>
                        </div>
                        <div className="progress-bar" style={{ backgroundColor: progressStatus.backgroundColor }}>
                          <div
                            className="progress-fill"
                            style={{
                              width: `${percentage}%`,
                              backgroundColor: progressStatus.color,
                              transition: "all 0.5s ease-in-out",
                            }}
                          />
                        </div>
                        <p
                          className="progress-status"
                          style={{
                            color: progressStatus.color,
                            marginTop: "6px",
                            fontSize: "0.85em",
                            fontWeight: "600",
                          }}
                        >
                          {progressStatus.status}
                        </p>
                      </div>
                    );
                  })}
              </div>

              {/* Total Score Box */}
              <div className="total-score-box">
                <h4>Total Score</h4>
                <div className="total-score-display">
                  <span className="total-score-value">
                    {scoringResult.score || 0}
                  </span>
                  <span className="total-score-max">/100</span>
                </div>
                <div className="confidence-meter">
                  <p className="confidence-label">
                    AI Confidence:{" "}
                    {((scoringResult.data?.confidence || 0) * 100).toFixed(1)}%
                  </p>
                  <div className="confidence-bar">
                    <div
                      className="confidence-fill"
                      style={{
                        width: `${(scoringResult.data?.confidence || 0) * 100}%`,
                      }}
                    />
                  </div>
                </div>
                <p className="overall-feedback">
                  {scoringResult.data?.feedback || ""}
                </p>
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
        selectedRubricTitle={selectedRubric?.title}
        isReadOnly={!selectedRubric?.isCustom}
        apiUrl={apiUrl}
      />
    </div>
  );
};

export default ScorerPage;
