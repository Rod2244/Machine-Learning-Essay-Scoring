import React, { useState, useEffect } from 'react';
import { Routes, Route, useNavigate, useLocation, Navigate } from 'react-router-dom';
import Topnavbar from './assets/Components/topnavbar';
import ScorerPage from './assets/pages/ScorerPage';
import RubricsSection from './assets/pages/RubricsSection';
import HistoryPage from './assets/pages/HistoryPage';
import LoginPage from './assets/pages/LoginPage';
import Home from './assets/Landing-Page/LP-pages/home';
import AboutUs from './assets/Landing-Page/LP-pages/about-us';
import ContactUs from './assets/Landing-Page/LP-pages/contact-us';
import './index.css';

// Protected Route Component
const ProtectedRoute = ({ user, children }) => {
  if (!user) {
    return <Navigate to="/login" replace />;
  }
  return children;
};

const App = () => {
  const [user, setUser] = useState(null);
  const [activeTab, setActiveTab] = useState('essays');
  const navigate = useNavigate();
  const location = useLocation();

  // ✅ Restore session from localStorage on page load/refresh
  useEffect(() => {
    const sessionToken = localStorage.getItem('session_token');
    const userId = localStorage.getItem('user_id');
    const userFullName = localStorage.getItem('user_full_name');
    const userEmail = localStorage.getItem('user_email');
    
    console.log('🔄 App mounting - checking localStorage...');
    console.log('   session_token exists:', !!sessionToken);
    console.log('   user_id:', userId);
    console.log('   user_full_name:', userFullName);
    console.log('   user_email:', userEmail);
    
    if (sessionToken && userId && userFullName && userEmail) {
      console.log('✅ Session restored from localStorage!');
      setUser({
        id: userId,
        name: userFullName,
        email: userEmail,
      });
    } else {
      console.log('⚠️ No complete session in localStorage');
    }
  }, []);

  const handleLogin = (userData) => {
    const userObj = {
      id: userData.user_id || userData.id,
      name: userData.name || userData.full_name,
      email: userData.email,
    };
    setUser(userObj);
    navigate('/essays');
  };

  const handleLogout = () => {
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_full_name');
    setUser(null);
    setActiveTab('essays');
    navigate('/');
    console.log('✓ Logged out and cleared session');
  };

  // Update activeTab based on URL path
  useEffect(() => {
    if (location.pathname === '/essays') {
      setActiveTab('essays');
    } else if (location.pathname === '/rubrics') {
      setActiveTab('rubrics');
    } else if (location.pathname === '/history') {
      setActiveTab('history');
    }
  }, [location.pathname]);

  // Navigation handler for landing pages with URL update
  const handleNavigation = (page) => {
    switch (page) {
      case 'home':
        navigate('/');
        break;
      case 'about':
        navigate('/about');
        break;
      case 'contact':
        navigate('/contact');
        break;
      default:
        navigate('/');
    }
  };

  // If user is logged in, show main app with tabs
  if (user) {
    return (
      <div className="app-container">
        <Topnavbar user={user} onLogout={handleLogout} />
        <div className="main-layout">
          {/* Notebook Tabs */}
          <div className="notebook-tabs-container">
            <div
              className={`notebook-tab ${activeTab === 'essays' ? 'active' : ''}`}
              onClick={() => navigate('/essays')}
            >
              <span className="icon">📝</span>
              <span className="label">Essays</span>
            </div>
            <div
              className={`notebook-tab ${activeTab === 'rubrics' ? 'active' : ''}`}
              onClick={() => navigate('/rubrics')}
            >
              <span className="icon">📋</span>
              <span className="label">Rubrics</span>
            </div>
            <div
              className={`notebook-tab ${activeTab === 'history' ? 'active' : ''}`}
              onClick={() => navigate('/history')}
            >
              <span className="icon">📚</span>
              <span className="label">History</span>
            </div>
          </div>

          {/* Outer Frame */}
          <div className="outer-frame">
            <div className="inner-workspace">
              <Routes>
                <Route path="/essays" element={<ProtectedRoute user={user}><ScorerPage /></ProtectedRoute>} />
                <Route path="/rubrics" element={<ProtectedRoute user={user}><RubricsSection /></ProtectedRoute>} />
                <Route path="/history" element={<ProtectedRoute user={user}><HistoryPage /></ProtectedRoute>} />
                <Route path="*" element={<Navigate to="/essays" replace />} />
              </Routes>
            </div>
          </div>
        </div>
      </div>
    );
  }

  // If user is not logged in, check if they're trying to access landing pages or show login
  const isLandingPage = location.pathname === '/' || location.pathname === '/about' || location.pathname === '/contact';

  if (isLandingPage) {
    return (
      <Routes>
        <Route path="/" element={<Home onNavigate={handleNavigation} />} />
        <Route path="/about" element={<AboutUs onNavigate={handleNavigation} />} />
        <Route path="/contact" element={<ContactUs onNavigate={handleNavigation} />} />
      </Routes>
    );
  }

  // Show login/signup pages for any other routes when not logged in
  return (
    <Routes>
      <Route path="/login" element={<LoginPage onLogin={handleLogin} />} />
      <Route path="/signup" element={<LoginPage onLogin={handleLogin} />} />
      {/* Redirect protected routes to login if not authenticated */}
      <Route path="/essays" element={<Navigate to="/login" replace />} />
      <Route path="/rubrics" element={<Navigate to="/login" replace />} />
      <Route path="/history" element={<Navigate to="/login" replace />} />
      <Route path="*" element={<Navigate to="/login" replace />} />
    </Routes>
  );
};

export default App;