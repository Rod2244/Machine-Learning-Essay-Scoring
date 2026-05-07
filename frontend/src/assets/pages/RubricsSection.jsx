import React, { useState, useEffect } from "react";
import "../css/RubricsSection.css";
import RubricsEditsec from "./RubricsEditsec";

// Default rubrics na built-in, hindi pwedeng i-delete
const INITIAL_RUBRICS = [
  {
    id: 1,
    icon: "📝",
    title: "Argumentative Essay",
    description:
      "Evaluates thesis statement, evidence quality, logical reasoning, and counterarguments",
    isCustom: false,
    criteria: [
      {
        name: "Thesis",
        description: "Clear and compelling thesis statement",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Thesis is clear, specific, and compelling",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Thesis is clear and mostly specific",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Thesis is present but vague or general",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Thesis is unclear or missing",
          },
        ],
      },
      {
        name: "Evidence",
        description: "Quality and relevance of supporting evidence",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Evidence is relevant, credible, and well-integrated",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Evidence is mostly relevant and credible",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Some evidence provided but may lack credibility",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Little to no credible evidence provided",
          },
        ],
      },
      {
        name: "Structure",
        description: "Organization and logical flow of argument",
        points: 30,
        levels: [
          {
            label: "Excellent",
            score: 30,
            descriptor: "Structure is logical with clear progression",
          },
          {
            label: "Proficient",
            score: 22,
            descriptor: "Generally logical structure with minor issues",
          },
          {
            label: "Developing",
            score: 15,
            descriptor: "Some organizational issues that affect clarity",
          },
          {
            label: "Beginning",
            score: 7,
            descriptor: "Weak or confusing organizational structure",
          },
        ],
      },
      {
        name: "Grammar",
        description: "Spelling, punctuation, and grammatical accuracy",
        points: 20,
        levels: [
          {
            label: "Excellent",
            score: 20,
            descriptor: "Virtually no grammatical or mechanical errors",
          },
          {
            label: "Proficient",
            score: 15,
            descriptor: "Minor errors that do not impede understanding",
          },
          {
            label: "Developing",
            score: 10,
            descriptor: "Several errors that occasionally distract",
          },
          {
            label: "Beginning",
            score: 5,
            descriptor: "Frequent errors that impede comprehension",
          },
        ],
      },
    ],
  },
  {
    id: 2,
    icon: "📋",
    title: "Expository Essay",
    description:
      "Assesses clarity, organization, research integration, and explanatory power",
    isCustom: false,
    criteria: [
      {
        name: "Clarity",
        description: "Clarity and accessibility of explanation",
        points: 30,
        levels: [
          {
            label: "Excellent",
            score: 30,
            descriptor: "Explanation is crystal clear and accessible",
          },
          {
            label: "Proficient",
            score: 22,
            descriptor: "Generally clear with minor unclear passages",
          },
          {
            label: "Developing",
            score: 15,
            descriptor: "Some clarity issues that affect understanding",
          },
          {
            label: "Beginning",
            score: 7,
            descriptor: "Explanation is often unclear or confusing",
          },
        ],
      },
      {
        name: "Organization",
        description: "Logical arrangement of ideas and transitions",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Ideas are well-organized with seamless transitions",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Generally organized with adequate transitions",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Some organizational issues but still followable",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Disorganized with poor transitions",
          },
        ],
      },
      {
        name: "Research",
        description: "Integration and citation of research sources",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Research is well-integrated and properly cited",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Research is integrated with mostly proper citations",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Some research used with citation issues",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Minimal research or poor citation practices",
          },
        ],
      },
      {
        name: "Grammar",
        description: "Spelling, punctuation, and grammatical accuracy",
        points: 20,
        levels: [
          {
            label: "Excellent",
            score: 20,
            descriptor: "Virtually no grammatical or mechanical errors",
          },
          {
            label: "Proficient",
            score: 15,
            descriptor: "Minor errors that do not impede understanding",
          },
          {
            label: "Developing",
            score: 10,
            descriptor: "Several errors that occasionally distract",
          },
          {
            label: "Beginning",
            score: 5,
            descriptor: "Frequent errors that impede comprehension",
          },
        ],
      },
    ],
  },
  {
    id: 3,
    icon: "📚",
    title: "Narrative Essay",
    description:
      "Measures storytelling elements, character development, and emotional engagement",
    isCustom: false,
    criteria: [
      {
        name: "Storytelling",
        description: "Plot development and narrative engagement",
        points: 30,
        levels: [
          {
            label: "Excellent",
            score: 30,
            descriptor: "Story is compelling with excellent plot development",
          },
          {
            label: "Proficient",
            score: 22,
            descriptor: "Story is interesting with good plot progression",
          },
          {
            label: "Developing",
            score: 15,
            descriptor: "Story is present but may lack engagement",
          },
          {
            label: "Beginning",
            score: 7,
            descriptor: "Story is confusing or poorly developed",
          },
        ],
      },
      {
        name: "Characters",
        description: "Character development and depth",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Characters are vivid and well-developed",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Characters are clear with adequate development",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Characters are present but underdeveloped",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Characters are flat or poorly defined",
          },
        ],
      },
      {
        name: "Engagement",
        description: "Emotional impact and reader connection",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Creates strong emotional connection with reader",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Creates some emotional engagement",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Minimal emotional impact or connection",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Little to no emotional engagement",
          },
        ],
      },
      {
        name: "Language",
        description: "Descriptive language and imagery",
        points: 20,
        levels: [
          {
            label: "Excellent",
            score: 20,
            descriptor: "Rich, vivid language with strong imagery",
          },
          {
            label: "Proficient",
            score: 15,
            descriptor: "Good descriptive language with clear imagery",
          },
          {
            label: "Developing",
            score: 10,
            descriptor: "Some descriptive language but lacks vividness",
          },
          {
            label: "Beginning",
            score: 5,
            descriptor: "Minimal descriptive language or imagery",
          },
        ],
      },
    ],
  },
  {
    id: 4,
    icon: "🔬",
    title: "Research Paper",
    description:
      "Evaluates research depth, citation quality, analysis, and academic rigor",
    isCustom: false,
    criteria: [
      {
        name: "Research",
        description: "Depth and quality of research conducted",
        points: 30,
        levels: [
          {
            label: "Excellent",
            score: 30,
            descriptor: "Research is thorough, well-sourced, and credible",
          },
          {
            label: "Proficient",
            score: 22,
            descriptor: "Research is solid with credible sources",
          },
          {
            label: "Developing",
            score: 15,
            descriptor: "Some research present but may lack depth",
          },
          {
            label: "Beginning",
            score: 7,
            descriptor: "Minimal or superficial research",
          },
        ],
      },
      {
        name: "Citations",
        description: "Proper citation format and accuracy",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "All citations are accurate and properly formatted",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Most citations are accurate and well-formatted",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Some citation errors or inconsistencies",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Many citation errors or missing citations",
          },
        ],
      },
      {
        name: "Analysis",
        description: "Critical analysis and interpretation",
        points: 25,
        levels: [
          {
            label: "Excellent",
            score: 25,
            descriptor: "Analysis is deep, critical, and insightful",
          },
          {
            label: "Proficient",
            score: 18,
            descriptor: "Good analysis with some critical thinking",
          },
          {
            label: "Developing",
            score: 12,
            descriptor: "Some analysis but mostly descriptive",
          },
          {
            label: "Beginning",
            score: 6,
            descriptor: "Minimal analysis or mostly summary",
          },
        ],
      },
      {
        name: "Rigor",
        description: "Academic standards and scholarly approach",
        points: 20,
        levels: [
          {
            label: "Excellent",
            score: 20,
            descriptor: "High academic rigor and scholarly standards",
          },
          {
            label: "Proficient",
            score: 15,
            descriptor: "Good academic standards and approach",
          },
          {
            label: "Developing",
            score: 10,
            descriptor: "Meets basic academic standards",
          },
          {
            label: "Beginning",
            score: 5,
            descriptor: "Does not meet academic standards",
          },
        ],
      },
    ],
  },
];

// Mga emoji choices para sa custom rubric icon picker
const ICON_OPTIONS = [
  "✍️",
  "🧠",
  "💡",
  "📖",
  "🎯",
  "🖊️",
  "📰",
  "🗂️",
  "🏛️",
  "🌐",
];

const RubricsSection = () => {
  const [rubrics, setRubrics] = useState([]);
  const [selectedRubric, setSelectedRubric] = useState(null);
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState("");
  const [newDesc, setNewDesc] = useState("");
  const [newIcon, setNewIcon] = useState("✍️");
  const [showDeleteConfirmModal, setShowDeleteConfirmModal] = useState(false);
  const [rubricToDelete, setRubricToDelete] = useState(null);
  const [deleteSuccess, setDeleteSuccess] = useState(false);

  // Fetch rubrics from backend on mount
  const fetchRubrics = async () => {
    try {
      const response = await fetch("http://localhost:5000/api/rubrics");
      const data = await response.json();

      // Merge INITIAL_RUBRICS with fetched custom rubrics
      // Ensure pre-defined rubrics have isCustom: false, and custom ones have isCustom: true
      const mergedRubrics = [
        ...INITIAL_RUBRICS,
        ...(Array.isArray(data)
          ? data
              .filter(
                (r) => !INITIAL_RUBRICS.some((initial) => initial.id === r.id),
              )
              .map((r) => ({
                ...r,
                isCustom: r.isCustom !== false ? true : false,
              }))
          : []),
      ];

      setRubrics(mergedRubrics);
    } catch (err) {
      console.error("Failed to fetch rubrics:", err);
      // Fallback to initial rubrics if fetch fails
      setRubrics(INITIAL_RUBRICS);
    }
  };

  useEffect(() => {
    fetchRubrics();
  }, []);

  // Save rubric edits to backend
  const handleSave = async (data) => {
    if (!selectedRubric || !selectedRubric.id) return;

    // Prevent saving pre-defined rubrics (they are read-only)
    if (!selectedRubric.isCustom) {
      alert("Cannot update pre-defined rubrics. They are read-only.");
      setSelectedRubric(null);
      return;
    }

    // Prepare updated rubric with full criteria details including all scoring levels
    const updatedRubric = {
      title: data.title,
      description: selectedRubric.description,
      icon: selectedRubric.icon,
      isCustom: true,
      criteria: data.criteria.map((c) => ({
        name: c.name,
        description: c.description,
        points: Math.max(...c.levels.map((l) => l.score)),
        levels: c.levels.map((l) => ({
          label: l.label,
          score: l.score,
          descriptor: l.descriptor,
        })),
      })),
    };

    console.log("📤 Sending update to backend:", {
      id: selectedRubric.id,
      rubric: updatedRubric,
    });

    try {
      const response = await fetch(
        `http://localhost:5000/api/rubrics/${selectedRubric.id}`,
        {
          method: "PATCH",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(updatedRubric),
        },
      );

      console.log("📥 Response status:", response.status);
      const result = await response.json();
      console.log("📥 Response data:", result);

      if (!result.success) {
        alert("Failed to update rubric: " + (result.error || "Unknown error"));
      } else {
        alert("✅ Rubric updated successfully!");
        // Refetch the specific rubric to get the latest data from database
        try {
          const fetchResponse = await fetch(
            `http://localhost:5000/api/rubrics/${selectedRubric.id}`,
          );
          const fetchResult = await fetchResponse.json();
          console.log("📥 Refetched rubric:", fetchResult);

          if (fetchResult.rubric) {
            // Mark it as custom if it's a user-created rubric
            fetchResult.rubric.isCustom = true;
            // Update the rubric in the list
            setRubrics((prevRubrics) =>
              prevRubrics.map((r) =>
                r.id === selectedRubric.id ? fetchResult.rubric : r,
              ),
            );
            console.log("✅ Updated rubric in state with fresh database data");
          }
        } catch (refetchErr) {
          console.error("Error refetching updated rubric:", refetchErr);
          // If refetch fails, still refresh the entire list
          fetchRubrics();
        }
      }
    } catch (err) {
      alert("Failed to update rubric: " + err.message);
      console.error("Update error:", err);
    }
    setSelectedRubric(null);
  };

  // Add new custom essay type and save to backend
  const handleAddEssayType = async () => {
    if (!newTitle.trim()) return;
    const user_id = localStorage.getItem("user_id");
    const newRubric = {
      icon: newIcon,
      title: newTitle.trim(),
      description: newDesc.trim() || "Custom essay type rubric",
      isCustom: true,
      criteria: [
        {
          name: "Content",
          description: "Clarity and depth of ideas",
          points: 25,
          levels: [
            {
              label: "Excellent",
              score: 25,
              descriptor: "Clear, focused, and thoroughly developed",
            },
            {
              label: "Proficient",
              score: 18,
              descriptor: "Mostly clear with adequate development",
            },
            {
              label: "Developing",
              score: 12,
              descriptor: "Present but lacks depth or focus",
            },
            {
              label: "Beginning",
              score: 6,
              descriptor: "Unclear or poorly developed",
            },
          ],
        },
        {
          name: "Organization",
          description: "Logical flow and structure",
          points: 25,
          levels: [
            {
              label: "Excellent",
              score: 25,
              descriptor: "Logical and transitions are seamless",
            },
            {
              label: "Proficient",
              score: 18,
              descriptor: "Generally organized with adequate transitions",
            },
            {
              label: "Developing",
              score: 12,
              descriptor: "Some organization but flow is inconsistent",
            },
            {
              label: "Beginning",
              score: 6,
              descriptor: "Little to no organizational structure",
            },
          ],
        },
        {
          name: "Language",
          description: "Vocabulary and sentence variety",
          points: 25,
          levels: [
            {
              label: "Excellent",
              score: 25,
              descriptor: "Rich vocabulary and varied sentence structures",
            },
            {
              label: "Proficient",
              score: 18,
              descriptor: "Adequate vocabulary with some variety",
            },
            {
              label: "Developing",
              score: 12,
              descriptor: "Limited vocabulary and repetitive structures",
            },
            {
              label: "Beginning",
              score: 6,
              descriptor: "Very limited language control",
            },
          ],
        },
        {
          name: "Grammar",
          description: "Spelling, punctuation, and accuracy",
          points: 25,
          levels: [
            {
              label: "Excellent",
              score: 25,
              descriptor: "Virtually no grammatical or mechanical errors",
            },
            {
              label: "Proficient",
              score: 18,
              descriptor: "Minor errors that do not impede understanding",
            },
            {
              label: "Developing",
              score: 12,
              descriptor: "Several errors that occasionally distract",
            },
            {
              label: "Beginning",
              score: 6,
              descriptor: "Frequent errors that impede comprehension",
            },
          ],
        },
      ],
      created_by: user_id,
    };

    // Save to backend
    try {
      const response = await fetch("http://localhost:5000/api/rubrics", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(newRubric),
      });
      const data = await response.json();
      if (data.success && data.rubric) {
        setRubrics((prev) => [...prev, { ...newRubric, id: data.rubric.id }]);
        // Optionally show a success message
      } else {
        alert("Failed to save rubric: " + (data.error || "Unknown error"));
      }
    } catch (err) {
      alert("Failed to save rubric: " + err.message);
    }

    // Reset form fields
    setNewTitle("");
    setNewDesc("");
    setNewIcon("✍️");
    setShowAddModal(false);
    // Agad i-edit yung bagong rubric
    setSelectedRubric(newRubric);
  };

  const handleDelete = (rubric, e) => {
    // Pigilan yung card click pag delete ang pinindot
    e.stopPropagation();
    setRubricToDelete(rubric);
    setShowDeleteConfirmModal(true);
  };

  const handleConfirmDelete = async () => {
    if (!rubricToDelete || !rubricToDelete.id) return;

    try {
      const response = await fetch(
        `http://localhost:5000/api/rubrics/${rubricToDelete.id}`,
        {
          method: "DELETE",
          headers: { "Content-Type": "application/json" },
        },
      );

      const result = await response.json();
      console.log("Delete response:", result);

      if (result.success) {
        // Remove from local state
        setRubrics((prev) => prev.filter((r) => r.id !== rubricToDelete.id));

        // Show success message
        setDeleteSuccess(true);
        setShowDeleteConfirmModal(false);
        setRubricToDelete(null);

        // Auto-hide success message after 3 seconds
        setTimeout(() => {
          setDeleteSuccess(false);
        }, 3000);
      } else {
        alert("Failed to delete rubric: " + (result.error || "Unknown error"));
      }
    } catch (err) {
      alert("Failed to delete rubric: " + err.message);
      console.error("Delete error:", err);
    }
  };

  const handleCancelDelete = () => {
    setShowDeleteConfirmModal(false);
    setRubricToDelete(null);
  };

  if (selectedRubric) {
    return (
      <RubricsEditsec
        rubric={selectedRubric}
        onSave={handleSave}
        onCancel={() => setSelectedRubric(null)}
        isReadOnly={!selectedRubric.isCustom}
      />
    );
  }

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Rubrics</h2>
        <p>Select an essay type to view and edit its scoring criteria</p>
      </div>

      <div className="rubrics-grid">
        {rubrics.map((rubric) => {
          const total = rubric.criteria.reduce((sum, c) => sum + c.points, 0);
          return (
            <div
              key={rubric.id}
              className="rubric-item clickable"
              onClick={() => setSelectedRubric(rubric)}
              role="button"
              tabIndex={0}
              onKeyDown={(e) => e.key === "Enter" && setSelectedRubric(rubric)}
            >
              {/* Delete button — visible lang sa mga custom rubrics */}
              {rubric.isCustom && (
                <button
                  type="button"
                  className="rubric-delete-btn"
                  onClick={(e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    handleDelete(rubric, e);
                  }}
                  title="Delete rubric"
                >
                  ✕
                </button>
              )}

              <span className="rubric-icon">{rubric.icon}</span>
              <h3>{rubric.title}</h3>
              <p>{rubric.description}</p>

              {/* Criteria breakdown — makita agad ang pts per criterion */}
              <div className="rubric-criteria-pills">
                {rubric.criteria.map((c, i) => (
                  <span key={i} className="rubric-criteria-pill">
                    {c.name} <strong>{c.points}pts</strong>
                  </span>
                ))}
              </div>

              {/* Total score badge sa baba */}
              <div className="rubric-total-badge">Total: {total} pts</div>

              <span className="rubric-edit-hint">
                {rubric.isCustom
                  ? "Click to edit criteria →"
                  : "View criteria (Read-Only) →"}
              </span>
            </div>
          );
        })}

        {/* Add Essay Type card — laging nasa dulo 
        <div
          className="rubric-item rubric-add-card"
          onClick={() => setShowAddModal(true)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === "Enter" && setShowAddModal(true)}
        >
          <span className="rubric-add-icon">＋</span>
          <h3>Add Essay Type</h3>
          <p>Create a custom rubric for a new essay type</p>
        </div> */}
      </div>

      {/* Modal para mag-add ng bagong essay type */}
      {showAddModal && (
        <div className="modal-overlay" onClick={() => setShowAddModal(false)}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">New Essay Type</h3>

            {/* Icon picker — piliin ang icon ng rubric */}
            <label className="modal-label">Choose an icon</label>
            <div className="modal-icon-picker">
              {ICON_OPTIONS.map((icon) => (
                <button
                  key={icon}
                  className={`modal-icon-btn ${newIcon === icon ? "active" : ""}`}
                  onClick={() => setNewIcon(icon)}
                >
                  {icon}
                </button>
              ))}
            </div>

            <label className="modal-label">Essay Type Name</label>
            <input
              className="modal-input"
              placeholder="e.g. Persuasive Essay"
              value={newTitle}
              onChange={(e) => setNewTitle(e.target.value)}
            />

            <label className="modal-label">
              Description <span className="modal-optional">(optional)</span>
            </label>
            <input
              className="modal-input"
              placeholder="What will this rubric evaluate?"
              value={newDesc}
              onChange={(e) => setNewDesc(e.target.value)}
            />

            <div className="modal-footer">
              <button
                className="modal-cancel-btn"
                onClick={() => setShowAddModal(false)}
              >
                Cancel
              </button>
              <button
                className="modal-create-btn"
                onClick={handleAddEssayType}
                disabled={!newTitle.trim()}
              >
                Create & Edit Rubric
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Delete confirmation modal */}
      {showDeleteConfirmModal && rubricToDelete && (
        <div className="modal-overlay" onClick={handleCancelDelete}>
          <div className="modal-box" onClick={(e) => e.stopPropagation()}>
            <h3 className="modal-title">Delete Rubric</h3>
            <p className="modal-delete-message">
              Are you sure you want to delete "
              <strong>{rubricToDelete.title}</strong>"? This action cannot be
              undone.
            </p>

            <div className="modal-footer">
              <button className="modal-cancel-btn" onClick={handleCancelDelete}>
                Cancel
              </button>
              <button
                className="modal-delete-confirm-btn"
                onClick={handleConfirmDelete}
              >
                Delete Permanently
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Success notification popup */}
      {deleteSuccess && (
        <div className="success-notification">
          <span className="success-icon">✓</span>
          <p>Rubric deleted successfully!</p>
        </div>
      )}
    </div>
  );
};

export default RubricsSection;
