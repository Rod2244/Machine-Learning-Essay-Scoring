import React, { useState } from 'react';
import '../css/RubricsEditsec.css';

// Default criteria — ginagamit pag walang existing criteria ang rubric
const DEFAULT_CRITERIA = [
  {
    id: 1, name: 'Content & Ideas',
    description: 'Clarity and depth of main argument and supporting points.',
    levels: [
      { label: 'Excellent',  score: 30, descriptor: 'Ideas are clear, focused, and thoroughly developed.' },
      { label: 'Proficient', score: 22, descriptor: 'Ideas are mostly clear with adequate development.' },
      { label: 'Developing', score: 15, descriptor: 'Ideas are present but lack depth or focus.' },
      { label: 'Beginning',  score: 8,  descriptor: 'Ideas are unclear or poorly developed.' },
    ],
  },
  {
    id: 2, name: 'Organization',
    description: 'Logical flow, coherent structure, and effective transitions.',
    levels: [
      { label: 'Excellent',  score: 25, descriptor: 'Structure is logical and transitions are seamless.' },
      { label: 'Proficient', score: 18, descriptor: 'Generally organized with adequate transitions.' },
      { label: 'Developing', score: 12, descriptor: 'Some organization but flow is inconsistent.' },
      { label: 'Beginning',  score: 6,  descriptor: 'Little to no organizational structure.' },
    ],
  },
  {
    id: 3, name: 'Language & Style',
    description: 'Vocabulary, sentence variety, and appropriate tone.',
    levels: [
      { label: 'Excellent',  score: 25, descriptor: 'Rich vocabulary and varied sentence structures.' },
      { label: 'Proficient', score: 18, descriptor: 'Adequate vocabulary with some sentence variety.' },
      { label: 'Developing', score: 12, descriptor: 'Limited vocabulary and repetitive structures.' },
      { label: 'Beginning',  score: 6,  descriptor: 'Very limited language control.' },
    ],
  },
  {
    id: 4, name: 'Grammar & Mechanics',
    description: 'Spelling, punctuation, and grammatical accuracy.',
    levels: [
      { label: 'Excellent',  score: 20, descriptor: 'Virtually no grammatical or mechanical errors.' },
      { label: 'Proficient', score: 15, descriptor: 'Minor errors that do not impede understanding.' },
      { label: 'Developing', score: 10, descriptor: 'Several errors that occasionally distract.' },
      { label: 'Beginning',  score: 5,  descriptor: 'Frequent errors that impede comprehension.' },
    ],
  },
];

// Tinatanggap na yung `rubric` prop para ma-pre-fill ang title ng selected essay type
const RubricsEditsec = ({ rubric, onSave, onCancel }) => {
  const [criteria, setCriteria] = useState(DEFAULT_CRITERIA);
  const [expandedId, setExpandedId] = useState(null);

  // Gamitin ang title ng piniling rubric, hindi hardcoded
  const [rubricTitle, setRubricTitle] = useState(rubric?.title || 'Essay Scoring Rubric');

  const maxTotal = criteria.reduce(
    (sum, c) => sum + Math.max(...c.levels.map(l => l.score)), 0
  );

  const updateCriterion = (id, field, value) =>
    setCriteria(prev => prev.map(c => c.id === id ? { ...c, [field]: value } : c));

  const updateLevel = (cId, li, field, value) =>
    setCriteria(prev => prev.map(c =>
      c.id === cId
        ? { ...c, levels: c.levels.map((l, i) => i === li ? { ...l, [field]: value } : l) }
        : c
    ));

  const addCriterion = () => {
    const id = Date.now();
    setCriteria(prev => [...prev, {
      id, name: '', description: '',
      levels: [
        { label: 'Excellent',  score: 10, descriptor: '' },
        { label: 'Proficient', score: 7,  descriptor: '' },
        { label: 'Developing', score: 4,  descriptor: '' },
        { label: 'Beginning',  score: 1,  descriptor: '' },
      ],
    }]);
    // Auto-expand yung bagong criterion
    setExpandedId(id);
  };

  const deleteCriterion = (id) => {
    setCriteria(prev => prev.filter(c => c.id !== id));
    if (expandedId === id) setExpandedId(null);
  };

  const move = (i, dir) => {
    const next = [...criteria];
    const t = i + dir;
    if (t < 0 || t >= next.length) return;
    [next[i], next[t]] = [next[t], next[i]];
    setCriteria(next);
  };

  return (
    <div className="re-container">
      <div className="re-header">
        <div className="re-header-left">
          {/* Editable yung title — makikita yung essay type name dito */}
          <input
            className="re-title-input"
            value={rubricTitle}
            onChange={e => setRubricTitle(e.target.value)}
            placeholder="Rubric Title"
          />
          <p className="re-subtitle">Click a criterion to expand and edit its scoring levels.</p>
        </div>
        {/* Total points badge — auto-calculate habang nag-eEdit */}
        <div className="re-score-badge">
          <span className="re-score-num">{maxTotal}</span>
          <span className="re-score-label">total pts</span>
        </div>
      </div>

      <div className="re-criteria-list">
        {criteria.map((c, i) => (
          <div key={c.id} className={`re-card ${expandedId === c.id ? 'expanded' : ''}`}>
            {/* I-click para palawakin o i-collapse ang criterion */}
            <div className="re-card-top" onClick={() => setExpandedId(expandedId === c.id ? null : c.id)}>
              <div className="re-card-left">
                <span className="re-card-index">{String(i + 1).padStart(2, '0')}</span>
                <div className="re-card-info">
                  <span className="re-card-name">{c.name || <em>Untitled Criterion</em>}</span>
                  {expandedId !== c.id && (
                    <span className="re-card-desc-preview">{c.description || 'No description'}</span>
                  )}
                </div>
              </div>
              <div className="re-card-right">
                {/* Score pills — quick view ng pts per level */}
                <div className="re-level-pills">
                  {c.levels.map((l, li) => (
                    <span key={li} className={`re-level-pill re-level-pill--${li}`}>{l.score}</span>
                  ))}
                </div>
                <span className="re-chevron">{expandedId === c.id ? '▲' : '▼'}</span>
              </div>
            </div>

            {expandedId === c.id && (
              <div className="re-card-body">
                <div className="re-top-fields">
                  <div className="re-field-row">
                    <label className="re-field-label">Criterion Name</label>
                    <input
                      className="re-field-input"
                      value={c.name}
                      onChange={e => updateCriterion(c.id, 'name', e.target.value)}
                      placeholder="e.g. Content & Ideas"
                    />
                  </div>
                  <div className="re-field-row">
                    <label className="re-field-label">Description</label>
                    <input
                      className="re-field-input"
                      value={c.description}
                      onChange={e => updateCriterion(c.id, 'description', e.target.value)}
                      placeholder="What does this criterion evaluate?"
                    />
                  </div>
                </div>

                {/* Scoring levels — 4 columns: Excellent, Proficient, Developing, Beginning */}
                <div className="re-levels-section">
                  <p className="re-levels-heading">Scoring Levels</p>
                  <div className="re-levels-grid">
                    {c.levels.map((l, li) => (
                      <div key={li} className={`re-level-card re-level-card--${li}`}>
                        <div className="re-level-header">
                          <input
                            className="re-level-label-input"
                            value={l.label}
                            onChange={e => updateLevel(c.id, li, 'label', e.target.value)}
                          />
                          <input
                            className="re-level-score-input"
                            type="number"
                            min={0}
                            value={l.score}
                            onChange={e => updateLevel(c.id, li, 'score', Number(e.target.value))}
                          />
                          <span className="re-level-pts">pts</span>
                        </div>
                        <textarea
                          className="re-level-descriptor"
                          rows={3}
                          value={l.descriptor}
                          onChange={e => updateLevel(c.id, li, 'descriptor', e.target.value)}
                          placeholder="Describe performance at this level..."
                        />
                      </div>
                    ))}
                  </div>
                </div>

                {/* Move up/down at delete — para ma-reorder or matanggal ang criterion */}
                <div className="re-card-actions">
                  <button className="re-move-btn" onClick={() => move(i, -1)} disabled={i === 0}>↑</button>
                  <button className="re-move-btn" onClick={() => move(i, 1)} disabled={i === criteria.length - 1}>↓</button>
                  <button className="re-delete-btn" onClick={() => deleteCriterion(c.id)}>🗑 Delete</button>
                </div>
              </div>
            )}
          </div>
        ))}
      </div>

      <button className="re-add-btn" onClick={addCriterion}>
        <span className="re-add-icon">+</span> Add Criterion
      </button>

      <div className="re-footer">
        <button className="re-cancel-btn" onClick={onCancel}>Cancel</button>
        {/* I-pass lahat ng data pataas — title + criteria */}
        <button className="re-save-btn" onClick={() => onSave?.({ title: rubricTitle, criteria })}>
          Save Rubric
        </button>
      </div>
    </div>
  );
};

export default RubricsEditsec;