import React, { useState } from 'react';
import Topnavbar from './assets/Components/topnavbar';
import ScorerPage from './assets/pages/ScorerPage';
import RubricsSection from './assets/pages/RubricsSection';
import HistoryPage from './assets/pages/HistoryPage';
import LoginPage from './assets/pages/LoginPage';
import Home from './assets/Landing-Page/LP-pages/home';
import AboutUs from './assets/Landing-Page/LP-pages/about-us';
import ContactUs from './assets/Landing-Page/LP-pages/contact-us';
import './index.css';

const App = () => {
  const [user, setUser] = useState(null); // null = not logged in
  const [activeTab, setActiveTab] = useState('essays');
  const [showLanding, setShowLanding] = useState(true); // Show landing page by default
  const [currentPage, setCurrentPage] = useState('home'); // Track current landing page

  // ✅ Restore session from localStorage on page load/refresh
  React.useEffect(() => {
    const sessionToken = localStorage.getItem('session_token');
    const userId = localStorage.getItem('user_id');
    const userFullName = localStorage.getItem('user_full_name');
    
    console.log('🔄 App mounting - checking localStorage...');
    console.log('   session_token exists:', !!sessionToken);
    console.log('   user_id:', userId);
    console.log('   user_full_name:', userFullName);
    
    if (sessionToken && userId && userFullName) {
      // Session exists in localStorage, restore user login state
      console.log('✅ Session restored from localStorage!');
      setUser({
        id: userId,
        full_name: userFullName,
      });
    } else {
      console.log('⚠️ No complete session in localStorage');
      console.log('   Missing:', {
        session_token: !sessionToken,
        user_id: !userId,
        user_full_name: !userFullName
      });
    }
  }, []); // Run only once on mount

  // Listen for custom event to show landing page
  React.useEffect(() => {
    const handleShowLanding = () => {
      setShowLanding(true);
      setCurrentPage('home');
    };
    window.addEventListener('showLanding', handleShowLanding);
    return () => window.removeEventListener('showLanding', handleShowLanding);
  }, []);

  // Listen for custom event to show login page
  React.useEffect(() => {
    const handleShowLogin = () => {
      setShowLanding(false);
    };
    window.addEventListener('showLogin', handleShowLogin);
    return () => window.removeEventListener('showLogin', handleShowLogin);
  }, []);

  // Listen for custom event to show main app
  React.useEffect(() => {
    const handleShowMainApp = () => {
      if (user) {
        setShowLanding(false);
      } else {
        // If not logged in, show login page
        setShowLanding(false);
      }
    };
    window.addEventListener('showMainApp', handleShowMainApp);
    return () => window.removeEventListener('showMainApp', handleShowMainApp);
  }, [user]);

  // Handle navigation
  const handleNavigation = (page) => {
    if (page === 'home') {
      setShowLanding(true);
      setCurrentPage('home');
    } else if (page === 'about') {
      setShowLanding(true);
      setCurrentPage('about');
    } else if (page === 'contact') {
      setShowLanding(true);
      setCurrentPage('contact');
    }
  };

  // Listen for navigation events
  React.useEffect(() => {
    const handleNavigation = (e) => {
      handleNavigation(e.detail.page);
    };
    window.addEventListener('navigate', handleNavigation);
    return () => window.removeEventListener('navigate', handleNavigation);
  }, []);

  const renderLandingPage = () => {
    switch (currentPage) {
      case 'home':
        return <Home onNavigate={handleNavigation} />;
      case 'about':
        return <AboutUs onNavigate={handleNavigation} />;
      case 'contact':
        return <ContactUs onNavigate={handleNavigation} />;
      default:
        return <Home onNavigate={handleNavigation} />;
    }
  };

  const handleLogin = (userData) => {
    setUser(userData);
    setShowLanding(false); // Go to main app after login
  };

  const handleLogout = () => {
    // Clear localStorage when logging out
    localStorage.removeItem('session_token');
    localStorage.removeItem('user_id');
    localStorage.removeItem('user_full_name');
    
    setUser(null);
    setActiveTab('essays');
    setShowLanding(false); // Show login page after logout
    console.log('✓ Logged out and cleared session');
  };

  // Show landing page if requested
  if (showLanding) {
    return renderLandingPage();
  }

  // Show login page if not logged in
  if (!user) {
    return <LoginPage onLogin={handleLogin} />;
  }

  const renderPage = () => {
    switch (activeTab) {
      case 'essays':
        return <ScorerPage />;
      case 'rubrics':
        return <RubricsSection />;
      case 'history':
        return <HistoryPage />;
      default:
        return <ScorerPage />;
    }
  };

  return (
    <div className="app-container">
      <Topnavbar user={user} onLogout={handleLogout} />
      <div className="main-layout">
        {/* Notebook Tabs */}
        <div className="notebook-tabs-container">
          <div
            className={`notebook-tab ${activeTab === 'essays' ? 'active' : ''}`}
            onClick={() => setActiveTab('essays')}
          >
            <span className="icon">📝</span>
            <span className="label">Essays</span>
          </div>
          <div
            className={`notebook-tab ${activeTab === 'rubrics' ? 'active' : ''}`}
            onClick={() => setActiveTab('rubrics')}
          >
            <span className="icon">📋</span>
            <span className="label">Rubrics</span>
          </div>
          <div
            className={`notebook-tab ${activeTab === 'history' ? 'active' : ''}`}
            onClick={() => setActiveTab('history')}
          >
            <span className="icon">📚</span>
            <span className="label">History</span>
          </div>
        </div>

        {/* Outer Frame */}
        <div className="outer-frame">
          <div className="inner-workspace">
            {renderPage()}
          </div>
        </div>
      </div>
    </div>
  );
};

export default App;