import { useNavigate } from "react-router-dom";

export default function Home() {
  const navigate = useNavigate();

  return (
    <div className="home-container">
      {/* Background animated shapes */}
      <div className="bg-shapes">
        <div className="shape shape-1"></div>
        <div className="shape shape-2"></div>
        <div className="shape shape-3"></div>
      </div>

      {/* Main content with fade-in animation */}
      <div className="home-content fade-in">
        {/* Logo container and icon */}
        <div className="logo-container">
          <div className="logo-icon">
            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" strokeWidth="2"/>
              <path d="M12 12l-3 3 1.5 1.5 4-4" strokeWidth="2" fill="currentColor"/>
            </svg>
          </div>
        </div>

        {/* Titles and description */}
        <h1 className="hero-title">Welcome to <span className="gradient-text">MedSage</span></h1>
        <h2 className="hero-subtitle">AI-Powered Medical Diagnostic Assistant</h2>
        <p className="hero-description">
          Experience intelligent, guided diagnosis through conversational AI. Enter patient details and let our advanced system help identify potential conditions.
        </p>

        {/* Features grid */}
        <div className="feature-grid">
          <div className="feature-card">
            <div className="feature-icon">🤖</div>
            <h3>AI-Powered</h3>
            <p>Advanced diagnostic algorithms</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">💬</div>
            <h3>Conversational</h3>
            <p>Natural chat interface</p>
          </div>
          <div className="feature-card">
            <div className="feature-icon">📊</div>
            <h3>Comprehensive</h3>
            <p>Detailed PDF reports</p>
          </div>
          {/* New feature card */}
          <div className="feature-card">
            <div className="feature-icon">⚡</div>
            <h3>Instant Results</h3>
            <p>Real-time analysis & insights</p>
          </div>
        </div>

        {/* Call to action button */}
        <button onClick={() => navigate("/patient-info")} className="cta-button">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M5 12h14M12 5l7 7-7 7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Start Diagnosis</span>
        </button>

        {/* Trust badges */}
        <div className="trust-badges">
          <div className="badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" strokeWidth="2"/>
            </svg>
            Secure & Private
          </div>
          <div className="badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
              <polyline points="12 6 12 12 16 14" strokeWidth="2"/>
            </svg>
            Fast Diagnosis
          </div>
          <div className="badge">
            <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="20 6 9 17 4 12" strokeWidth="2"/>
            </svg>
            Evidence-Based
          </div>
        </div>
      </div>
    </div>
  );
}
