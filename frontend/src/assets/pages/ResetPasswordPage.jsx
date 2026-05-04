import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import '../css/ResetPasswordPage.css';
import { createClient } from '@supabase/supabase-js';

const ResetPasswordPage = () => {
  const navigate = useNavigate();
  const [newPassword, setNewPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [notification, setNotification] = useState(null);
  const [sessionValid, setSessionValid] = useState(false);

  // Initialize Supabase
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
  const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
  const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

  // Check if user has a valid recovery session
  useEffect(() => {
    const checkSession = async () => {
      if (!supabase) {
        setError('Supabase is not configured.');
        return;
      }

      try {
        const { data: { session }, error: sessionError } = await supabase.auth.getSession();

        if (sessionError) {
          setError('Session error: ' + sessionError.message);
          return;
        }

        if (!session) {
          // Try to get session from URL hash (recovery token)
          const hash = window.location.hash;
          if (hash.includes('type=recovery')) {
            setSessionValid(true);
          } else {
            setError('Invalid or expired recovery link. Please request a new password reset.');
            setTimeout(() => navigate('/login'), 3000);
          }
        } else {
          setSessionValid(true);
        }
      } catch (err) {
        setError('Failed to verify session: ' + err.message);
      }
    };

    checkSession();
  }, [supabase, navigate]);

  const handleResetPassword = async (e) => {
    e.preventDefault();
    setError('');

    if (!newPassword) {
      setError('Please enter a new password');
      return;
    }
    if (newPassword.length < 6) {
      setError('Password must be at least 6 characters');
      return;
    }
    if (newPassword !== confirmPassword) {
      setError('Passwords do not match');
      return;
    }

    if (!supabase) {
      setError('Supabase is not configured.');
      return;
    }

    setLoading(true);

    try {
      const { error: updateError } = await supabase.auth.updateUser({
        password: newPassword,
      });

      if (updateError) {
        setError('Error: ' + updateError.message);
        setNotification({
          type: 'error',
          title: '❌ Update Failed',
          message: updateError.message,
        });
      } else {
        setNotification({
          type: 'success',
          title: '✅ Password Updated',
          message: 'Your password has been successfully updated! Redirecting to login...',
        });
        setTimeout(() => {
          navigate('/login');
        }, 2500);
      }
    } catch (err) {
      setError(err.message || 'Failed to update password');
      setNotification({
        type: 'error',
        title: '❌ Error',
        message: err.message || 'Failed to update password',
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="reset-page">
      {/* Decorative background blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />

      <div className="reset-card">
        {/* Back Button */}
        <button className="reset-back-btn" onClick={() => navigate('/')} title="Back to Landing Page">
          ← Back
        </button>

        {/* Brand */}
        <div className="reset-brand">
          <span className="reset-logo-icon">🎓</span>
          <h1 className="reset-logo-text">AcadScore</h1>
        </div>

        {error && !sessionValid ? (
          <div className="reset-error-state">
            <div className="error-icon">❌</div>
            <h3>Invalid Recovery Link</h3>
            <p>{error}</p>
            <button className="back-to-login-btn" onClick={() => navigate('/login')}>
              Back to Login
            </button>
          </div>
        ) : sessionValid ? (
          <>
            <h2 className="reset-title">🔑 Set New Password</h2>
            <p className="reset-subtitle">Enter your new password below to regain access to your account.</p>

            {/* API Error Message */}
            {error && (
              <div className="api-error-msg" style={{
                backgroundColor: '#fee',
                color: '#c00',
                padding: '10px 12px',
                borderRadius: '6px',
                marginBottom: '15px',
                fontSize: '14px',
                border: '1px solid #fcc'
              }}>
                {error}
              </div>
            )}

            <form onSubmit={handleResetPassword} className="reset-form" noValidate>
              {/* New Password */}
              <div className="form-field">
                <label className="form-label" htmlFor="newPassword">New Password</label>
                <div className="password-wrapper">
                  <input
                    id="newPassword"
                    type={showPassword ? 'text' : 'password'}
                    className={`form-input ${error ? 'error' : ''}`}
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value);
                      setError('');
                    }}
                    required
                  />
                  <button
                    type="button"
                    className="show-password-btn"
                    onClick={() => setShowPassword(p => !p)}
                    aria-label="Toggle password visibility"
                  >
                    {showPassword ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div className="form-field">
                <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
                <div className="password-wrapper">
                  <input
                    id="confirmPassword"
                    type={showConfirmPassword ? 'text' : 'password'}
                    className={`form-input ${error ? 'error' : ''}`}
                    placeholder="••••••••"
                    value={confirmPassword}
                    onChange={(e) => {
                      setConfirmPassword(e.target.value);
                      setError('');
                    }}
                    required
                  />
                  <button
                    type="button"
                    className="show-password-btn"
                    onClick={() => setShowConfirmPassword(p => !p)}
                    aria-label="Toggle confirm password visibility"
                  >
                    {showConfirmPassword ? (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M1 12s4-8 11-8 11 8 11 8-4 8-11 8-11-8-11-8z"/>
                        <circle cx="12" cy="12" r="3"/>
                      </svg>
                    ) : (
                      <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2">
                        <path d="M17.94 17.94A10.07 10.07 0 0 1 12 20c-7 0-11-8-11-8a18.45 18.45 0 0 1 5.06-5.94M9.9 4.24A9.12 9.12 0 0 1 12 4c7 0 11 8 11 8a18.5 18.5 0 0 1-2.16 3.19m-6.72-1.07a3 3 0 1 1-4.24-4.24"/>
                        <line x1="1" y1="1" x2="23" y2="23"/>
                      </svg>
                    )}
                  </button>
                </div>
              </div>

              <button 
                type="submit" 
                className={`submit-btn ${loading ? 'loading' : ''}`} 
                disabled={loading}
              >
                {loading ? <span className="loading-dots"><span /><span /><span /></span> : 'Update Password'}
              </button>

              <p className="back-link">
                Remember your password?{' '}
                <button type="button" className="link-btn" onClick={() => navigate('/login')}>
                  Log in
                </button>
              </p>
            </form>
          </>
        ) : (
          <div className="loading-state">
            <div className="loading-spinner">⏳</div>
            <h3>Verifying recovery link...</h3>
            <p>Please wait while we verify your password reset request.</p>
          </div>
        )}
      </div>

      {/* Success Notification */}
      {notification && notification.type === 'success' && (
        <div className="success-notification">
          <span className="success-icon">{notification.title.split(' ')[0]}</span>
          <div className="success-content">
            <p className="success-title">{notification.title}</p>
            <p className="success-message">{notification.message}</p>
          </div>
        </div>
      )}

      {/* Error Notification */}
      {notification && notification.type === 'error' && (
        <div className="error-notification">
          <span className="error-icon">{notification.title.split(' ')[0]}</span>
          <div className="error-content">
            <p className="error-title">{notification.title}</p>
            <p className="error-message">{notification.message}</p>
          </div>
        </div>
      )}
    </div>
  );
};

export default ResetPasswordPage;
