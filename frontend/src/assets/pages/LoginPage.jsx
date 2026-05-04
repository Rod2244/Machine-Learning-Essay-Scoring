import React, { useState, useEffect } from 'react';
import { useNavigate, useLocation } from 'react-router-dom';
import '../css/LoginPage.css';
import { createClient } from '@supabase/supabase-js';

const LoginPage = ({ onLogin }) => {
  const navigate = useNavigate();
  const location = useLocation();
  const [mode, setMode] = useState('login'); // 'login' or 'signup'
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    password: '',
    confirmPassword: '',
  });
  const [errors, setErrors] = useState({});
  const [loading, setLoading] = useState(false);
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);
  const [apiError, setApiError] = useState('');
  const [successMessage, setSuccessMessage] = useState('');

  // Forgot password states
  const [showForgotModal, setShowForgotModal] = useState(false);
  const [forgotEmail, setForgotEmail] = useState('');
  const [forgotLoading, setForgotLoading] = useState(false);
  const [forgotError, setForgotError] = useState('');
  const [showResetModal, setShowResetModal] = useState(false);
  const [newPassword, setNewPassword] = useState('');
  const [confirmNewPassword, setConfirmNewPassword] = useState('');
  const [showNewPassword, setShowNewPassword] = useState(false);
  const [showConfirmNewPassword, setShowConfirmNewPassword] = useState(false);
  const [resetLoading, setResetLoading] = useState(false);
  const [resetError, setResetError] = useState('');
  const [notification, setNotification] = useState(null); // { type, title, message }

  // Initialize Supabase
  const supabaseUrl = import.meta.env.VITE_SUPABASE_URL;
  const supabaseKey = import.meta.env.VITE_SUPABASE_ANON_KEY;
  const supabase = supabaseUrl && supabaseKey ? createClient(supabaseUrl, supabaseKey) : null;

  const API_BASE_URL = 'http://localhost:5000'; // Change if backend is on different port

  // Force light mode on login page
  useEffect(() => {
    // Remove dark-mode class if it exists
    document.documentElement.classList.remove('dark-mode');
  }, []);

  // Sync mode with URL
  useEffect(() => {
    if (location.pathname === '/signup') {
      setMode('signup');
    } else {
      setMode('login');
    }
  }, [location.pathname]);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) setErrors(prev => ({ ...prev, [name]: '' }));
    if (apiError) setApiError('');
  };

  const validate = () => {
    const newErrors = {};
    if (mode === 'signup' && !formData.name.trim()) {
      newErrors.name = 'Name is required';
    }
    if (!formData.email.trim()) {
      newErrors.email = 'Email is required';
    } else if (!/\S+@\S+\.\S+/.test(formData.email)) {
      newErrors.email = 'Enter a valid email';
    }
    if (!formData.password) {
      newErrors.password = 'Password is required';
    } else if (formData.password.length < 6) {
      newErrors.password = 'At least 6 characters';
    }
    if (mode === 'signup' && formData.password !== formData.confirmPassword) {
      newErrors.confirmPassword = 'Passwords do not match';
    }
    return newErrors;
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    const newErrors = validate();
    if (Object.keys(newErrors).length > 0) {
      setErrors(newErrors);
      return;
    }

    setLoading(true);
    setApiError('');

    try {
      if (mode === 'signup') {
        // Call signup endpoint
        const response = await fetch(`${API_BASE_URL}/api/signup`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            full_name: formData.name,
            email: formData.email,
            password: formData.password,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          setApiError(data.error || 'Signup failed. Please try again.');
          setLoading(false);
          return;
        }

        // Signup successful
        console.log('✓ Signup successful:', data);
        setLoading(false);
        
        // Show success message
        setSuccessMessage(`✓ Account created successfully! Welcome, ${formData.name}. Redirecting to login...`);
        
        // Clear form
        setFormData({ name: '', email: '', password: '', confirmPassword: '' });
        setErrors({});
        setApiError('');
        
        // Redirect to login after 2.5 seconds
        setTimeout(() => {
          setSuccessMessage('');
          setMode('login');
        }, 2500);
      } else {
        // Call login endpoint
        const response = await fetch(`${API_BASE_URL}/api/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: formData.email,
            password: formData.password,
          }),
        });

        const data = await response.json();

        if (!response.ok) {
          setApiError(data.error || 'Login failed. Please try again.');
          setLoading(false);
          return;
        }

        // Login successful - save token and user info
        console.log('✓ Login successful:', data);
        
        // Store session token and user info for future requests
        localStorage.setItem('session_token', data.session.access_token);
        localStorage.setItem('user_email', data.user.email);
        localStorage.setItem('user_id', data.user.id);
        localStorage.setItem('user_full_name', data.user.full_name || data.user.email.split('@')[0]);
        
        // ✅ Verify localStorage was set correctly
        console.log('✓ Stored in localStorage:');
        console.log('   user_id:', localStorage.getItem('user_id'));
        console.log('   user_full_name:', localStorage.getItem('user_full_name'));
        console.log('   session_token exists:', !!localStorage.getItem('session_token'));
        
        onLogin({
          name: data.user.full_name || data.user.email.split('@')[0],
          email: data.user.email,
          user_id: data.user.id,
          session: data.session,
        });
        setLoading(false);
      }
    } catch (error) {
      console.error('API Error:', error);
      setApiError(error.message || 'Connection error. Make sure backend is running on port 5000.');
      setLoading(false);
    }
  };

  const switchMode = () => {
    const newMode = mode === 'login' ? 'signup' : 'login';
    navigate(newMode === 'signup' ? '/signup' : '/login');
    setFormData({ name: '', email: '', password: '', confirmPassword: '' });
    setErrors({});
    setApiError('');
  };

  // Forgot password: Step 1 - Send reset email
  const handleForgotPassword = async (e) => {
    e.preventDefault();
    if (!forgotEmail.trim()) {
      setForgotError('Please enter your email address');
      return;
    }

    if (!supabase) {
      setForgotError('Supabase is not configured. Check environment variables.');
      return;
    }

    setForgotLoading(true);
    setForgotError('');

    try {
      const { error } = await supabase.auth.resetPasswordForEmail(forgotEmail, {
        redirectTo: `${window.location.origin}/reset-password`,
      });

      if (error) {
        setForgotError('Error: ' + error.message);
        setNotification({
          type: 'error',
          title: '❌ Reset Failed',
          message: error.message,
        });
      } else {
        setNotification({
          type: 'success',
          title: '📧 Email Sent',
          message: `Password reset link sent to ${forgotEmail}. Check your email!`,
        });
        setTimeout(() => setNotification(null), 4000);
        setForgotEmail('');
        setShowForgotModal(false);
      }
    } catch (err) {
      setForgotError(err.message || 'Failed to send reset email');
      setNotification({
        type: 'error',
        title: '❌ Error',
        message: err.message || 'Failed to send reset email',
      });
    } finally {
      setForgotLoading(false);
    }
  };

  // Reset password: Step 2 - Update password
  const handleResetPassword = async (e) => {
    e.preventDefault();

    if (!newPassword) {
      setResetError('Please enter a new password');
      return;
    }
    if (newPassword.length < 6) {
      setResetError('Password must be at least 6 characters');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      setResetError('Passwords do not match');
      return;
    }

    if (!supabase) {
      setResetError('Supabase is not configured.');
      return;
    }

    setResetLoading(true);
    setResetError('');

    try {
      const { error } = await supabase.auth.updateUser({
        password: newPassword,
      });

      if (error) {
        setResetError('Error: ' + error.message);
        setNotification({
          type: 'error',
          title: '❌ Update Failed',
          message: error.message,
        });
      } else {
        setNotification({
          type: 'success',
          title: '✅ Password Updated',
          message: 'Your password has been successfully updated! Redirecting to login...',
        });
        setTimeout(() => {
          setNotification(null);
          setShowResetModal(false);
          setNewPassword('');
          setConfirmNewPassword('');
          navigate('/login');
        }, 2000);
      }
    } catch (err) {
      setResetError(err.message || 'Failed to update password');
      setNotification({
        type: 'error',
        title: '❌ Error',
        message: err.message || 'Failed to update password',
      });
    } finally {
      setResetLoading(false);
    }
  };

  return (
    <div className="login-page">
      {/* Decorative background blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />

      <div className="login-card">
        {/* Back Button - Inside container */}
        <button className="login-back-btn" onClick={() => navigate('/')} title="Back to Landing Page">
          ← Back
        </button>

        {/* Brand */}
        <div className="login-brand">
          <span className="login-logo-icon">🎓</span>
          <h1 className="login-logo-text">AcadScore</h1>
        </div>

        {/* Mode Toggle */}
        <div className="mode-toggle">
          <button
            className={`toggle-btn ${mode === 'login' ? 'active' : ''}`}
            onClick={() => navigate('/login')}
            type="button"
            disabled={successMessage ? true : false}
          >
            Log In
          </button>
          <button
            className={`toggle-btn ${mode === 'signup' ? 'active' : ''}`}
            onClick={() => navigate('/signup')}
            type="button"
            disabled={successMessage ? true : false}
          >
            Sign Up
          </button>
        </div>

        <p className="login-subtitle">
          {mode === 'login'
            ? 'Welcome back! Enter your details to continue.'
            : 'Create your account to get started.'}
        </p>

        {/* API Error Message */}
        {apiError && (
          <div className="api-error-msg" style={{
            backgroundColor: '#fee',
            color: '#c00',
            padding: '10px 12px',
            borderRadius: '6px',
            marginBottom: '15px',
            fontSize: '14px',
            border: '1px solid #fcc'
          }}>
            {apiError}
          </div>
        )}

        {/* Success Message */}
        {successMessage && (
          <div className="api-success-msg" style={{
            backgroundColor: '#efe',
            color: '#060',
            padding: '10px 12px',
            borderRadius: '6px',
            marginBottom: '15px',
            fontSize: '14px',
            border: '1px solid #cfc',
            textAlign: 'center',
            fontWeight: '500'
          }}>
            {successMessage}
          </div>
        )}

        <form onSubmit={handleSubmit} className="login-form" noValidate disabled={successMessage ? true : false}>
          {/* Name field — signup only */}
          <div className={`form-field ${mode === 'signup' ? 'visible' : 'hidden'}`}>
            <label className="form-label" htmlFor="name">Full Name</label>
            <input
              id="name"
              name="name"
              type="text"
              className={`form-input ${errors.name ? 'error' : ''}`}
              placeholder="e.g. Maria Santos"
              value={formData.name}
              onChange={handleChange}
              autoComplete="name"
            />
            {errors.name && <span className="error-msg">{errors.name}</span>}
          </div>

          {/* Email */}
          <div className="form-field visible">
            <label className="form-label" htmlFor="email">Email Address</label>
            <input
              id="email"
              name="email"
              type="email"
              className={`form-input ${errors.email ? 'error' : ''}`}
              placeholder="you@example.com"
              value={formData.email}
              onChange={handleChange}
              autoComplete="email"
            />
            {errors.email && <span className="error-msg">{errors.email}</span>}
          </div>

          {/* Password */}
          <div className="form-field visible">
            <label className="form-label" htmlFor="password">Password</label>
            <div className="password-wrapper">
              <input
                id="password"
                name="password"
                type={showPassword ? 'text' : 'password'}
                className={`form-input ${errors.password ? 'error' : ''}`}
                placeholder="••••••••"
                value={formData.password}
                onChange={handleChange}
                autoComplete={mode === 'login' ? 'current-password' : 'new-password'}
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
            {errors.password && <span className="error-msg">{errors.password}</span>}
          </div>

          {/* Confirm Password — signup only */}
          <div className={`form-field ${mode === 'signup' ? 'visible' : 'hidden'}`}>
            <label className="form-label" htmlFor="confirmPassword">Confirm Password</label>
            <div className="password-wrapper">
              <input
                id="confirmPassword"
                name="confirmPassword"
                type={showConfirmPassword ? 'text' : 'password'}
                className={`form-input ${errors.confirmPassword ? 'error' : ''}`}
                placeholder="••••••••"
                value={formData.confirmPassword}
                onChange={handleChange}
                autoComplete="new-password"
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
            {errors.confirmPassword && <span className="error-msg">{errors.confirmPassword}</span>}
          </div>

          {/* Forgot password hint */}
          {mode === 'login' && (
            <div className="forgot-row">
              <button 
                type="button" 
                className="forgot-btn"
                onClick={() => setShowForgotModal(true)}
              >
                Forgot password?
              </button>
            </div>
          )}

          <button type="submit" className={`submit-btn ${loading || successMessage ? 'loading' : ''}`} disabled={loading || successMessage ? true : false}>
            {loading
              ? <span className="loading-dots"><span /><span /><span /></span>
              : mode === 'login' ? 'Log In' : 'Create Account'}
          </button>
        </form>

        <p className="switch-prompt">
          {mode === 'login' ? "Don't have an account? " : 'Already have an account? '}
          <button type="button" className="switch-btn" onClick={switchMode} disabled={successMessage ? true : false}>
            {mode === 'login' ? 'Sign up' : 'Log in'}
          </button>
        </p>
      </div>

      {/* Forgot Password Modal - Step 1: Enter Email */}
      {showForgotModal && (
        <div className="modal-overlay" onClick={() => setShowForgotModal(false)}>
          <div className="forgot-modal" onClick={e => e.stopPropagation()}>
            <h3 className="forgot-modal-title">🔐 Reset Password</h3>
            <p className="forgot-modal-subtitle">Enter your email address and we'll send you a password reset link.</p>

            <form onSubmit={handleForgotPassword} className="forgot-form">
              <div className="form-field">
                <label className="form-label" htmlFor="forgotEmail">Email Address</label>
                <input
                  id="forgotEmail"
                  type="email"
                  className={`form-input ${forgotError ? 'error' : ''}`}
                  placeholder="you@example.com"
                  value={forgotEmail}
                  onChange={(e) => {
                    setForgotEmail(e.target.value);
                    setForgotError('');
                  }}
                  required
                />
                {forgotError && <span className="error-msg">{forgotError}</span>}
              </div>

              <div className="forgot-footer">
                <button
                  type="button"
                  className="modal-cancel-btn"
                  onClick={() => {
                    setShowForgotModal(false);
                    setForgotEmail('');
                    setForgotError('');
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="modal-confirm-btn"
                  disabled={forgotLoading}
                >
                  {forgotLoading ? '⏳ Sending...' : 'Send Reset Link'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Reset Password Modal - Step 2: Set New Password */}
      {showResetModal && (
        <div className="modal-overlay" onClick={() => setShowResetModal(false)}>
          <div className="forgot-modal" onClick={e => e.stopPropagation()}>
            <h3 className="forgot-modal-title">🔑 Set New Password</h3>
            <p className="forgot-modal-subtitle">Enter your new password below.</p>

            <form onSubmit={handleResetPassword} className="forgot-form">
              {/* New Password */}
              <div className="form-field">
                <label className="form-label" htmlFor="newPassword">New Password</label>
                <div className="password-wrapper">
                  <input
                    id="newPassword"
                    type={showNewPassword ? 'text' : 'password'}
                    className={`form-input ${resetError ? 'error' : ''}`}
                    placeholder="••••••••"
                    value={newPassword}
                    onChange={(e) => {
                      setNewPassword(e.target.value);
                      setResetError('');
                    }}
                    required
                  />
                  <button
                    type="button"
                    className="show-password-btn"
                    onClick={() => setShowNewPassword(p => !p)}
                  >
                    {showNewPassword ? '👁' : '👁‍🗨'}
                  </button>
                </div>
              </div>

              {/* Confirm Password */}
              <div className="form-field">
                <label className="form-label" htmlFor="confirmNewPassword">Confirm Password</label>
                <div className="password-wrapper">
                  <input
                    id="confirmNewPassword"
                    type={showConfirmNewPassword ? 'text' : 'password'}
                    className={`form-input ${resetError ? 'error' : ''}`}
                    placeholder="••••••••"
                    value={confirmNewPassword}
                    onChange={(e) => {
                      setConfirmNewPassword(e.target.value);
                      setResetError('');
                    }}
                    required
                  />
                  <button
                    type="button"
                    className="show-password-btn"
                    onClick={() => setShowConfirmNewPassword(p => !p)}
                  >
                    {showConfirmNewPassword ? '👁' : '👁‍🗨'}
                  </button>
                </div>
              </div>

              {resetError && <span className="error-msg">{resetError}</span>}

              <div className="forgot-footer">
                <button
                  type="button"
                  className="modal-cancel-btn"
                  onClick={() => {
                    setShowResetModal(false);
                    setNewPassword('');
                    setConfirmNewPassword('');
                    setResetError('');
                  }}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="modal-confirm-btn"
                  disabled={resetLoading}
                >
                  {resetLoading ? '⏳ Updating...' : 'Update Password'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {/* Success/Error Notification */}
      {notification && notification.type === 'success' && (
        <div className="success-notification">
          <span className="success-icon">{notification.title.split(' ')[0]}</span>
          <div className="success-content">
            <p className="success-title">{notification.title}</p>
            <p className="success-message">{notification.message}</p>
          </div>
        </div>
      )}

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

export default LoginPage;