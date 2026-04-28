import React, { useState, useEffect, useMemo } from 'react';
import '../css/HistoryPage.css';

const STATUSES = ['Graded', 'For Review', 'Returned'];

const ESSAY_TYPES = ['All Types', 'Argumentative Essay', 'Expository Essay', 'Narrative Essay', 'Research Paper'];

const getScoreColor = (score) => {
  if (score >= 90) return 'score-excellent';
  if (score >= 75) return 'score-good';
  if (score >= 60) return 'score-average';
  return 'score-poor';
};

const getScoreLabel = (score) => {
  if (score >= 90) return 'Excellent';
  if (score >= 75) return 'Good';
  if (score >= 60) return 'Average';
  return 'Needs Work';
};

const HistoryPage = () => {
  const [essays, setEssays] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  // Filters
  const [filterType, setFilterType] = useState('All Types');
  const [filterDate, setFilterDate] = useState('');
  const [search, setSearch] = useState('');

  // Sorting — column + direction
  const [sortCol, setSortCol] = useState('date');
  const [sortDir, setSortDir] = useState('desc');

  // Checkboxes for bulk actions
  const [selected, setSelected] = useState([]);

  // Modals
  const [viewEssay, setViewEssay] = useState(null);
  const [regradeEssay, setRegradeEssay] = useState(null);
  const [notesEssay, setNotesEssay] = useState(null);
  const [notesInput, setNotesInput] = useState('');

  const apiUrl = "http://localhost:5000";

  // Load essay history from Supabase
  useEffect(() => {
    const loadEssayHistory = async () => {
      try {
        setLoading(true);
        setError(null);

        // Get user_id from localStorage (set during login)
        const user_id = localStorage.getItem('user_id');
        if (!user_id) {
          setError('Please log in first to view your essay history');
          setLoading(false);
          return;
        }

        // Fetch only user's essays
        const response = await fetch(`${apiUrl}/api/essay-history?user_id=${user_id}`);
        const data = await response.json();

        if (data.success) {
          setEssays(data.essays || []);
        } else {
          setError(data.error || 'Failed to load essay history');
        }
      } catch (err) {
        console.error('Error loading history:', err);
        setError('Failed to connect to server');
      } finally {
        setLoading(false);
      }
    };

    loadEssayHistory();
  }, []);

  // Filter + search + sort
  const filtered = useMemo(() => {
    let list = essays.filter(e => {
      const matchType = filterType === 'All Types' || e.type === filterType;
      const matchDate = !filterDate || e.date === filterDate;
      const matchSearch = !search ||
        e.title.toLowerCase().includes(search.toLowerCase()) ||
        e.student.toLowerCase().includes(search.toLowerCase());
      return matchType && matchDate && matchSearch;
    });

    // Sort logic
    list = [...list].sort((a, b) => {
      let aVal, bVal;
      if (sortCol === 'date') { aVal = a.date; bVal = b.date; }
      else if (sortCol === 'score') { aVal = a.totalScore; bVal = b.totalScore; }
      else if (sortCol === 'student') { aVal = a.student; bVal = b.student; }
      else if (sortCol === 'status') { aVal = a.status; bVal = b.status; }
      if (aVal < bVal) return sortDir === 'asc' ? -1 : 1;
      if (aVal > bVal) return sortDir === 'asc' ? 1 : -1;
      return 0;
    });

    return list;
  }, [essays, filterType, filterDate, search, sortCol, sortDir]);

  // Toggle sort column
  const handleSort = (col) => {
    if (sortCol === col) setSortDir(d => d === 'asc' ? 'desc' : 'asc');
    else { setSortCol(col); setSortDir('asc'); }
  };

  const sortIcon = (col) => {
    if (sortCol !== col) return <span className="sort-icon inactive">↕</span>;
    return <span className="sort-icon active">{sortDir === 'asc' ? '↑' : '↓'}</span>;
  };

  // Checkbox logic
  const allChecked = filtered.length > 0 && filtered.every(e => selected.includes(e.id));
  const toggleAll = () => setSelected(allChecked ? [] : filtered.map(e => e.id));
  const toggleOne = (id) => setSelected(prev => prev.includes(id) ? prev.filter(x => x !== id) : [...prev, id]);

  // Bulk delete
  const handleBulkDelete = () => {
    setEssays(prev => prev.filter(e => !selected.includes(e.id)));
    setSelected([]);
  };

  // Status change
  const handleStatusChange = async (id, status) => {
    try {
      const response = await fetch(`${apiUrl}/api/essay-history/${id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ status }),
      });

      const data = await response.json();
      if (data.success) {
        setEssays(prev => prev.map(e => e.id === id ? { ...e, status } : e));
      } else {
        alert('Failed to update status');
      }
    } catch (err) {
      alert('Failed to update status');
    }
  };

  // Save notes
  const handleSaveNotes = async () => {
    try {
      const response = await fetch(`${apiUrl}/api/essay-history/${notesEssay.id}`, {
        method: 'PUT',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ 
          status: notesEssay.status,
          notes: notesInput 
        }),
      });

      const data = await response.json();
      if (data.success) {
        setEssays(prev => prev.map(e => e.id === notesEssay.id ? { ...e, notes: notesInput } : e));
        setNotesEssay(null);
      } else {
        alert('Failed to save notes');
      }
    } catch (err) {
      alert('Failed to save notes');
    }
  };

  // Re-grade: bump scores by small random delta (mock — sa real app, magbubukas ng grading form)
  const handleRegrade = (essay) => {
    setRegradeEssay(essay);
  };

  const confirmRegrade = () => {
    // Mock re-grade — just marks it as For Review para sa demo
    setEssays(prev => prev.map(e =>
      e.id === regradeEssay.id ? { ...e, status: 'For Review' } : e
    ));
    setRegradeEssay(null);
  };

  return (
    <div className="page-content">
      <div className="page-header">
        <h2>Essay History</h2>
        <p>View and manage previously graded essays</p>
      </div>

      {/* Search + Filters row */}
      <div className="history-toolbar">
        {/* Search bar */}
        <div className="search-wrap">
          <span className="search-icon">🔍</span>
          <input
            className="search-input"
            placeholder="Search by title or student..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
          {search && (
            <button className="search-clear" onClick={() => setSearch('')}>✕</button>
          )}
        </div>

        {/* Filters */}
        <div className="filter-group">
          <label className="filter-label">Type</label>
          <select className="filter-select" value={filterType} onChange={e => setFilterType(e.target.value)}>
            {ESSAY_TYPES.map(t => <option key={t}>{t}</option>)}
          </select>
        </div>
        <div className="filter-group">
          <label className="filter-label">Date</label>
          <input type="date" className="filter-select" value={filterDate} onChange={e => setFilterDate(e.target.value)} />
        </div>
        {(filterType !== 'All Types' || filterDate) && (
          <button className="filter-reset-btn" onClick={() => { setFilterType('All Types'); setFilterDate(''); }}>
            ✕ Clear
          </button>
        )}

        <span className="filter-count">{filtered.length} result{filtered.length !== 1 ? 's' : ''}</span>
      </div>

      {/* Bulk action bar — lumalabas pag may selected */}
      {selected.length > 0 && (
        <div className="bulk-bar">
          <span className="bulk-count">{selected.length} selected</span>
          <button className="bulk-delete-btn" onClick={handleBulkDelete}>🗑 Delete Selected</button>
          <button className="bulk-clear-btn" onClick={() => setSelected([])}>✕ Cancel</button>
        </div>
      )}

      {/* Table */}
      <div className="history-table-container">
        <div className="table-header-accent" />
        {loading ? (
          <div className="loading-state">
            <div className="loading-spinner">⏳</div>
            <h3>Loading essay history...</h3>
            <p>Fetching data from Supabase...</p>
          </div>
        ) : error ? (
          <div className="error-state">
            <div className="error-icon">❌</div>
            <h3>Error Loading Data</h3>
            <p>{error}</p>
            <button className="retry-btn" onClick={() => window.location.reload()}>Retry</button>
          </div>
        ) : filtered.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">🔍</div>
            <h3>No Results Found</h3>
            <p>Try adjusting your filters or search query.</p>
          </div>
        ) : (
          <table className="history-table">
            <colgroup>
              <col />{/* checkbox */}
              <col />{/* title */}
              <col />{/* student */}
              <col />{/* type */}
              <col />{/* date */}
              <col />{/* score */}
              <col />{/* remarks */}
              <col />{/* status */}
              <col />{/* actions */}
            </colgroup>
            <thead>
              <tr>
                {/* Select all checkbox */}
                <th className="th-check">
                  <input type="checkbox" checked={allChecked} onChange={toggleAll} />
                </th>
                <th>Essay Title</th>
                <th className="th-sortable" onClick={() => handleSort('student')}>
                  Student {sortIcon('student')}
                </th>
                <th>Type</th>
                <th className="th-sortable" onClick={() => handleSort('date')}>
                  Date {sortIcon('date')}
                </th>
                <th className="th-sortable" onClick={() => handleSort('score')}>
                  Score {sortIcon('score')}
                </th>
                <th>Remarks</th>
                <th className="th-sortable" onClick={() => handleSort('status')}>
                  Status {sortIcon('status')}
                </th>
                <th>Actions</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((essay, i) => (
                <tr
                  key={essay.id}
                  className={selected.includes(essay.id) ? 'row-selected' : ''}
                  style={{ animationDelay: `${i * 0.04}s` }}
                >
                  <td className="td-check">
                    <input
                      type="checkbox"
                      checked={selected.includes(essay.id)}
                      onChange={() => toggleOne(essay.id)}
                    />
                  </td>
                  <td className="essay-title-cell">
                    {essay.title}
                    {/* Notes indicator — may note icon pag may laman */}
                    {essay.notes && <span className="notes-indicator" title={essay.notes}>💬</span>}
                  </td>
                  <td className="essay-student-cell">
                    <span className="student-avatar">
                      {essay.student.split(' ').map(n => n[0]).join('').slice(0, 2)}
                    </span>
                    <span>{essay.student}</span>
                  </td>
                  <td>
                    <span className="essay-type-badge">{essay.type}</span>
                  </td>
                  <td className="essay-date-cell">
                    {new Date(essay.date).toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })}
                  </td>
                  <td>
                    <span className={`score-badge ${getScoreColor(essay.totalScore)}`}>
                      {essay.totalScore}/{essay.maxScore}
                    </span>
                  </td>
                  <td>
                    <span className={`remarks-badge ${getScoreColor(essay.totalScore)}`}>
                      {getScoreLabel(essay.totalScore)}
                    </span>
                  </td>
                  <td>
                    {/* Status dropdown — inline change */}
                    <select
                      className={`status-select status-${essay.status.replace(' ', '-').toLowerCase()}`}
                      value={essay.status}
                      onChange={e => handleStatusChange(essay.id, e.target.value)}
                    >
                      {STATUSES.map(s => <option key={s}>{s}</option>)}
                    </select>
                  </td>
                  <td>
                    <div className="action-btns">
                      <button className="action-btn view-btn" onClick={() => setViewEssay(essay)} title="View breakdown">
                        👁
                      </button>
                      <button className="action-btn regrade-btn" onClick={() => handleRegrade(essay)} title="Re-grade">
                        ✏️
                      </button>
                      <button
                        className="action-btn notes-btn"
                        onClick={() => { setNotesEssay(essay); setNotesInput(essay.notes); }}
                        title="Add notes"
                      >
                        💬
                      </button>
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>

      {/* Score Breakdown Modal */}
      {viewEssay && (
        <div className="modal-overlay" onClick={() => setViewEssay(null)}>
          <div className="breakdown-modal" onClick={e => e.stopPropagation()}>
            <div className="breakdown-header">
              <div>
                <h3 className="breakdown-title">{viewEssay.title}</h3>
                <p className="breakdown-meta">{viewEssay.student} · {viewEssay.type}</p>
              </div>
              <button className="breakdown-close" onClick={() => setViewEssay(null)}>✕</button>
            </div>
            <div className="breakdown-overall">
              <span className={`breakdown-score ${getScoreColor(viewEssay.totalScore)}`}>
                {viewEssay.totalScore}
              </span>
              <span className="breakdown-max">/ {viewEssay.maxScore}</span>
              <span className={`breakdown-label ${getScoreColor(viewEssay.totalScore)}`}>
                {getScoreLabel(viewEssay.totalScore)}
              </span>
            </div>
            <p className="breakdown-section-title">Score Breakdown</p>
            <div className="breakdown-criteria">
              {viewEssay.criteria.map((c, i) => {
                const pct = Math.round((c.score / c.max) * 100);
                return (
                  <div key={i} className="breakdown-criterion">
                    <div className="breakdown-criterion-top">
                      <span className="breakdown-criterion-name">{c.name}</span>
                      <span className="breakdown-criterion-score">{c.score}/{c.max}</span>
                    </div>
                    <div className="breakdown-bar-track">
                      <div className={`breakdown-bar-fill ${getScoreColor(pct)}`} style={{ width: `${pct}%` }} />
                    </div>
                  </div>
                );
              })}
            </div>
            {/* Show notes if may laman */}
            {viewEssay.notes && (
              <div className="breakdown-notes">
                <p className="breakdown-section-title">Teacher Notes</p>
                <p className="breakdown-notes-text">{viewEssay.notes}</p>
              </div>
            )}
          </div>
        </div>
      )}

      {/* Re-grade Confirmation Modal */}
      {regradeEssay && (
        <div className="modal-overlay" onClick={() => setRegradeEssay(null)}>
          <div className="confirm-modal" onClick={e => e.stopPropagation()}>
            <h3 className="confirm-title">Re-grade Essay?</h3>
            <p className="confirm-body">
              <strong>{regradeEssay.title}</strong> by {regradeEssay.student} will be opened for re-grading.
              The status will be set to "For Review".
            </p>
            <div className="confirm-footer">
              <button className="modal-cancel-btn" onClick={() => setRegradeEssay(null)}>Cancel</button>
              <button className="modal-confirm-btn" onClick={confirmRegrade}>Yes, Re-grade</button>
            </div>
          </div>
        </div>
      )}

      {/* Notes Modal */}
      {notesEssay && (
        <div className="modal-overlay" onClick={() => setNotesEssay(null)}>
          <div className="notes-modal" onClick={e => e.stopPropagation()}>
            <div className="breakdown-header">
              <div>
                <h3 className="breakdown-title">Teacher Notes</h3>
                <p className="breakdown-meta">{notesEssay.title}</p>
              </div>
              <button className="breakdown-close" onClick={() => setNotesEssay(null)}>✕</button>
            </div>
            <textarea
              className="notes-textarea"
              placeholder="Add private notes about this essay..."
              value={notesInput}
              onChange={e => setNotesInput(e.target.value)}
              rows={5}
            />
            <div className="confirm-footer">
              <button className="modal-cancel-btn" onClick={() => setNotesEssay(null)}>Cancel</button>
              <button className="modal-confirm-btn" onClick={handleSaveNotes}>Save Notes</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default HistoryPage;