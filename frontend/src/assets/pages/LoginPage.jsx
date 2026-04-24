import React, { useState } from 'react';
import '../css/LoginPage.css';

const LoginPage = ({ onLogin }) => {
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

  const API_BASE_URL = 'http://localhost:5000'; // Change if backend is on different port

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
    setMode(prev => prev === 'login' ? 'signup' : 'login');
    setFormData({ name: '', email: '', password: '', confirmPassword: '' });
    setErrors({});
    setApiError('');
  };

  return (
    <div className="login-page">
      {/* Decorative background blobs */}
      <div className="blob blob-1" />
      <div className="blob blob-2" />
      <div className="blob blob-3" />

      <div className="login-card">
        {/* Back Button - Inside container */}
        <button className="login-back-btn" onClick={() => window.dispatchEvent(new CustomEvent('showLanding'))} title="Back to Landing Page">
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
            onClick={() => setMode('login')}
            type="button"
            disabled={successMessage ? true : false}
          >
            Log In
          </button>
          <button
            className={`toggle-btn ${mode === 'signup' ? 'active' : ''}`}
            onClick={() => setMode('signup')}
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
              <button type="button" className="forgot-btn">Forgot password?</button>
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
    </div>
  );
};

export default LoginPage;