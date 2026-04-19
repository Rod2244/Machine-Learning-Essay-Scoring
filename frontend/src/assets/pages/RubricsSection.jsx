import React, { useState } from 'react';
import '../css/RubricsSection.css';
import RubricsEditsec from './RubricsEditsec';

// Default rubrics na built-in, hindi pwedeng i-delete
const INITIAL_RUBRICS = [
  {
    id: 1,
    icon: '📝',
    title: 'Argumentative Essay',
    description: 'Evaluates thesis statement, evidence quality, logical reasoning, and counterarguments',
    isCustom: false,
    criteria: [
      { name: 'Thesis', points: 25 },
      { name: 'Evidence', points: 25 },
      { name: 'Structure', points: 30 },
      { name: 'Grammar', points: 20 },
    ],
  },
  {
    id: 2,
    icon: '📋',
    title: 'Expository Essay',
    description: 'Assesses clarity, organization, research integration, and explanatory power',
    isCustom: false,
    criteria: [
      { name: 'Clarity', points: 30 },
      { name: 'Organization', points: 25 },
      { name: 'Research', points: 25 },
      { name: 'Grammar', points: 20 },
    ],
  },
  {
    id: 3,
    icon: '📚',
    title: 'Narrative Essay',
    description: 'Measures storytelling elements, character development, and emotional engagement',
    isCustom: false,
    criteria: [
      { name: 'Storytelling', points: 30 },
      { name: 'Characters', points: 25 },
      { name: 'Engagement', points: 25 },
      { name: 'Language', points: 20 },
    ],
  },
  {
    id: 4,
    icon: '🔬',
    title: 'Research Paper',
    description: 'Evaluates research depth, citation quality, analysis, and academic rigor',
    isCustom: false,
    criteria: [
      { name: 'Research', points: 30 },
      { name: 'Citations', points: 25 },
      { name: 'Analysis', points: 25 },
      { name: 'Rigor', points: 20 },
    ],
  },
];

// Mga emoji choices para sa custom rubric icon picker
const ICON_OPTIONS = ['✍️', '🧠', '💡', '📖', '🎯', '🖊️', '📰', '🗂️', '🏛️', '🌐'];

const RubricsSection = () => {
  const [rubrics, setRubrics] = useState(INITIAL_RUBRICS);
  const [selectedRubric, setSelectedRubric] = useState(null);

  // Para sa "Add Essay Type" modal
  const [showAddModal, setShowAddModal] = useState(false);
  const [newTitle, setNewTitle] = useState('');
  const [newDesc, setNewDesc] = useState('');
  const [newIcon, setNewIcon] = useState('✍️');

  // I-save yung edited rubric back sa list
  const handleSave = (data) => {
    setRubrics(prev =>
      prev.map(r => r.id === selectedRubric.id
        ? {
            ...r,
            title: data.title,
            criteria: data.criteria.map(c => ({
              name: c.name,
              points: Math.max(...c.levels.map(l => l.score)),
            })),
          }
        : r
      )
    );
    setSelectedRubric(null);
  };

  // Add new custom essay type
  const handleAddEssayType = () => {
    if (!newTitle.trim()) return;
    const newRubric = {
      id: Date.now(),
      icon: newIcon,
      title: newTitle.trim(),
      description: newDesc.trim() || 'Custom essay type rubric',
      isCustom: true,
      criteria: [
        { name: 'Content', points: 25 },
        { name: 'Organization', points: 25 },
        { name: 'Language', points: 25 },
        { name: 'Grammar', points: 25 },
      ],
    };
    setRubrics(prev => [...prev, newRubric]);
    // Reset form fields
    setNewTitle('');
    setNewDesc('');
    setNewIcon('✍️');
    setShowAddModal(false);
    // Agad i-edit yung bagong rubric
    setSelectedRubric(newRubric);
  };

  const handleDelete = (id, e) => {
    // Pigilan yung card click pag delete ang pinindot
    e.stopPropagation();
    setRubrics(prev => prev.filter(r => r.id !== id));
  };

  if (selectedRubric) {
    return (
      <RubricsEditsec
        rubric={selectedRubric}
        onSave={handleSave}
        onCancel={() => setSelectedRubric(null)}
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
              onKeyDown={(e) => e.key === 'Enter' && setSelectedRubric(rubric)}
            >
              {/* Delete button — visible lang sa mga custom rubrics */}
              {rubric.isCustom && (
                <button
                  className="rubric-delete-btn"
                  onClick={(e) => handleDelete(rubric.id, e)}
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

              <span className="rubric-edit-hint">Click to edit criteria →</span>
            </div>
          );
        })}

        {/* Add Essay Type card — laging nasa dulo */}
        <div
          className="rubric-item rubric-add-card"
          onClick={() => setShowAddModal(true)}
          role="button"
          tabIndex={0}
          onKeyDown={(e) => e.key === 'Enter' && setShowAddModal(true)}
        >
          <span className="rubric-add-icon">＋</span>
          <h3>Add Essay Type</h3>
          <p>Create a custom rubric for a new essay type</p>
        </div>
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
                  className={`modal-icon-btn ${newIcon === icon ? 'active' : ''}`}
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
              <button className="modal-cancel-btn" onClick={() => setShowAddModal(false)}>
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
    </div>
  );
};

export default RubricsSection;