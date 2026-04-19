import React, { useState, useEffect } from "react";
import "../css/confirmationModal.css";

const ConfirmationModal = ({
  isOpen,
  onClose,
  onSave,
  selectedRubricId = 1,
  apiUrl = "http://localhost:5000",
}) => {
  const [rubrics, setRubrics] = useState([
    { id: 1, name: "Grammar & Mechanics", score: "", maxScore: 100 },
    { id: 2, name: "Structure & Organization", score: "", maxScore: 100 },
    { id: 3, name: "Clarity & Style", score: "", maxScore: 100 },
  ]);
  const [saving, setSaving] = useState(false);

  // Load current rubric criteria when modal opens
  useEffect(() => {
    if (isOpen && selectedRubricId) {
      loadRubricCriteria();
    }
  }, [isOpen, selectedRubricId]);

  const loadRubricCriteria = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/rubrics`);
      if (response.ok) {
        const allRubrics = await response.json();
        const selectedRubric = allRubrics.find(
          (r) => r.id === selectedRubricId,
        );

        if (selectedRubric && selectedRubric.criteria) {
          // Convert backend criteria format to modal format
          const modalRubrics = selectedRubric.criteria.map(
            (criterion, idx) => ({
              id: idx + 1,
              name: criterion.name,
              score: "",
              maxScore: criterion.points,
            }),
          );
          setRubrics(modalRubrics);
        }
      }
    } catch (err) {
      console.error("Error loading rubric criteria:", err);
    }
  };

  const handleNameChange = (id, value) => {
    setRubrics((prev) =>
      prev.map((r) => (r.id === id ? { ...r, name: value } : r)),
    );
  };

  const handleScoreChange = (id, value) => {
    setRubrics((prev) =>
      prev.map((r) => (r.id === id ? { ...r, score: value } : r)),
    );
  };

  const handleMaxScoreChange = (id, value) => {
    setRubrics((prev) =>
      prev.map((r) => (r.id === id ? { ...r, maxScore: Number(value) } : r)),
    );
  };

  const handleAddRubric = () => {
    const newId = rubrics.length ? rubrics[rubrics.length - 1].id + 1 : 1;
    setRubrics((prev) => [
      ...prev,
      { id: newId, name: "", score: "", maxScore: 100 },
    ]);
  };

  const handleRemoveRubric = (id) => {
    setRubrics((prev) => prev.filter((r) => r.id !== id));
  };

  const handleSave = async () => {
    setSaving(true);
    try {
      // Convert modal format to backend format
      const customRubric = {
        id: selectedRubricId,
        criteria: rubrics.map((r) => ({
          name: r.name,
          points: r.maxScore,
        })),
      };

      const response = await fetch(`${apiUrl}/api/rubrics/save`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(customRubric),
      });

      if (response.ok) {
        if (onSave) onSave(rubrics);
        onClose();
      } else {
        alert("Failed to save rubric. Please try again.");
      }
    } catch (err) {
      console.error("Error saving rubric:", err);
      alert("Error saving rubric: " + err.message);
    } finally {
      setSaving(false);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="modal-header">
          <h2 className="modal-title">Edit Rubric Criteria</h2>
          <button
            className="modal-close-btn"
            onClick={onClose}
            disabled={saving}
          >
            ✕
          </button>
        </div>

        <p className="modal-subtitle">
          Customize rubric categories, enter the student's score, and set the
          maximum score.
        </p>

        {/* Column Labels */}
        <div className="modal-column-labels">
          <span className="col-label-name">Criteria</span>
          <span className="col-label-score">Score / Max</span>
        </div>

        {/* Rubric List */}
        <div className="modal-rubric-list">
          {rubrics.map((rubric, index) => (
            <div className="modal-rubric-row" key={rubric.id}>
              <span className="rubric-index">{index + 1}.</span>
              <input
                type="text"
                className="rubric-name-input"
                placeholder="Criteria name..."
                value={rubric.name}
                onChange={(e) => handleNameChange(rubric.id, e.target.value)}
                disabled={saving}
              />
              <div className="rubric-score-wrapper">
                <input
                  type="number"
                  className="rubric-score-input rubric-score-input--actual"
                  placeholder="0"
                  min={0}
                  max={rubric.maxScore}
                  value={rubric.score}
                  onChange={(e) => handleScoreChange(rubric.id, e.target.value)}
                  disabled={saving}
                />
                <span className="score-slash">/</span>
                <input
                  type="number"
                  className="rubric-score-input"
                  min={1}
                  max={999}
                  value={rubric.maxScore}
                  onChange={(e) =>
                    handleMaxScoreChange(rubric.id, e.target.value)
                  }
                  disabled={saving}
                />
              </div>
              <button
                className="rubric-remove-btn"
                onClick={() => handleRemoveRubric(rubric.id)}
                title="Remove criteria"
                disabled={saving}
              >
                🗑️
              </button>
            </div>
          ))}
        </div>

        {/* Add Criteria */}
        <button
          className="modal-add-btn"
          onClick={handleAddRubric}
          disabled={saving}
        >
          + Add Criteria
        </button>

        {/* Footer Buttons */}
        <div className="modal-footer">
          <button
            className="modal-cancel-btn"
            onClick={onClose}
            disabled={saving}
          >
            Cancel
          </button>
          <button
            className="modal-save-btn"
            onClick={handleSave}
            disabled={saving}
          >
            {saving ? "Saving..." : "Save Changes"}
          </button>
        </div>
      </div>
    </div>
  );
};

export default ConfirmationModal;
