import React, { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import { generatePDF, getNearestFacilities, extractSpecialist } from "../services/api";

export default function Summary() {
  const location = useLocation();
  const navigate = useNavigate();
  const { userDetails, chatHistory } = location.state || {};
  const [downloading, setDownloading] = useState(false);
  const [error, setError] = useState(null);
  
  const [pincode, setPincode] = useState("");
  const [showHospitals, setShowHospitals] = useState(false);
  const [hospitals, setHospitals] = useState([]);
  const [loadingHospitals, setLoadingHospitals] = useState(false);
  const [recommendedSpecialist, setRecommendedSpecialist] = useState("");

  if (!userDetails || !chatHistory) {
    return (
      <div className="error-container">
        <div className="error-card">
          <h2>No Summary Data Found</h2>
          <p>Please complete the diagnosis process first.</p>
          <button onClick={() => navigate("/")} className="cta-button">
            Go to Home
          </button>
        </div>
      </div>
    );
  }

  useEffect(() => {
    const getSpecialist = async () => {
      try {
        const response = await extractSpecialist(chatHistory);
        if (response.success && response.specialist) {
          setRecommendedSpecialist(response.specialist);
          console.log("Specialist extracted:", response.specialist);
        }
      } catch (err) {
        console.error("Error extracting specialist:", err);
      }
    };

    if (chatHistory && chatHistory.length > 0) {
      getSpecialist();
    }
  }, [chatHistory]);

  const handleFindHospitals = async () => {
    if (!pincode || pincode.length !== 6) {
      setError("Please enter a valid 6-digit pincode");
      return;
    }

    setLoadingHospitals(true);
    setError(null);

    try {
      const response = await getNearestFacilities(
        pincode,
        recommendedSpecialist,
        "all"
      );

      if (response.success) {
        setHospitals(response.search_links);
        setShowHospitals(true);
        console.log("Nearest facilities found");
      } else {
        setError(response.error);
      }
    } catch (err) {
      console.error("Error:", err);
      setError(err.message);
    } finally {
      setLoadingHospitals(false);
    }
  };

  const handleDownloadPDF = async () => {
    if (!chatHistory || chatHistory.length === 0) {
      setError("No conversation history to summarize");
      return;
    }

    setDownloading(true);
    setError(null);

    try {
      const payload = {
        user_details: {
          name: String(userDetails.name || ""),
          age: String(userDetails.age || ""),
          gender: String(userDetails.gender || ""),
          symptoms: String(userDetails.symptoms || "")
        },
        chat_history: chatHistory.map(msg => ({
          human: String(msg.human || ""),
          ai: String(msg.ai || "")
        }))
      };

      const response = await generatePDF(payload.user_details, payload.chat_history);
      
      const blob = new Blob([response.data], { type: "application/pdf" });
      const link = document.createElement("a");
      link.href = URL.createObjectURL(blob);
      link.download = `MedSage_Report_${userDetails?.name?.replace(/\s+/g, '_')}_${new Date().toISOString().split('T')[0]}.pdf`;
      link.click();
      URL.revokeObjectURL(link.href);
      
      console.log("PDF downloaded");
    } catch (err) {
      console.error("Error:", err);
      setError(err.message || "Failed to generate PDF");
    } finally {
      setDownloading(false);
    }
  };

  // ✅ NEW: Clear all data and start fresh diagnosis
  const handleNewDiagnosis = () => {
    sessionStorage.clear();
    localStorage.clear();
    navigate("/", { replace: true, state: {} });
    window.location.reload();
  };

  return (
    <div className="summary-page">
      <div className="summary-header">
        <button 
          onClick={() => navigate("/chat")} 
          className="back-button"
          aria-label="Back to chat"
        >
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M19 12H5M12 19l-7-7 7-7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
        </button>
        <div>
          <h1 className="summary-title">Diagnostic Summary</h1>
          <p className="summary-subtitle">Complete diagnosis report for {userDetails.name}</p>
        </div>
      </div>

      <div className="summary-container">
        {/* Patient Information */}
        <div className="detail-card">
          <div className="card-header">
            <h2 className="card-title">Patient Information</h2>
            <div className="card-badge">Verified</div>
          </div>
          <div className="detail-grid">
            <div className="detail-item">
              <span className="detail-label">Full Name</span>
              <span className="detail-value">{userDetails.name || "N/A"}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Date of Birth</span>
              <span className="detail-value">{userDetails.dob || "N/A"}</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Age</span>
              <span className="detail-value">{userDetails.age || "N/A"} years</span>
            </div>
            <div className="detail-item">
              <span className="detail-label">Gender</span>
              <span className="detail-value">{userDetails.gender || "N/A"}</span>
            </div>
            {userDetails.symptoms && (
              <div className="detail-item full-width">
                <span className="detail-label">Initial Symptoms</span>
                <span className="detail-value">{userDetails.symptoms}</span>
              </div>
            )}
          </div>
        </div>

        {/* Find Medical Facilities */}
        <div className="detail-card">
          <div className="card-header">
            <h2 className="card-title">Find Nearest Medical Facilities</h2>
            <span className="card-badge">📍 Location Based</span>
          </div>

          {recommendedSpecialist && (
            <div className="specialist-info">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <circle cx="12" cy="12" r="10" strokeWidth="2"/>
                <polyline points="12 16 16 12 12 8" strokeWidth="2" strokeLinecap="round"/>
              </svg>
              <p>Recommended Specialist: <strong>{recommendedSpecialist}</strong></p>
            </div>
          )}

          <div className="hospital-finder">
            <div className="hospital-search">
              <input
                type="text"
                placeholder="Enter your pincode (6 digits)"
                value={pincode}
                onChange={(e) => setPincode(e.target.value.replace(/\D/g, '').slice(0, 6))}
                maxLength="6"
                className="pincode-input"
                disabled={loadingHospitals}
              />
              <button
                onClick={handleFindHospitals}
                disabled={loadingHospitals || pincode.length !== 6}
                className="hospital-search-btn"
              >
                {loadingHospitals ? (
                  <>
                    <div className="btn-spinner"></div>
                    <span>Searching...</span>
                  </>
                ) : (
                  <>
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                      <circle cx="11" cy="11" r="8" strokeWidth="2"/>
                      <path d="m21 21-4.35-4.35" strokeWidth="2" strokeLinecap="round"/>
                    </svg>
                    <span>Find Facilities</span>
                  </>
                )}
              </button>
            </div>

            {showHospitals && (
              <div className="hospitals-list">
                <h3 className="hospitals-location">
                  📍 Nearest Facilities
                </h3>
                <div className="hospitals-grid-3columns">
                  <div className="facility-section">
                    <div className="facility-section-header">
                      <div className="facility-icon-bg hospital-bg">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M12 2C6.48 2 2 6.48 2 12s4.48 10 10 10 10-4.48 10-10S17.52 2 12 2zm0 18c-4.41 0-8-3.59-8-8s3.59-8 8-8 8 3.59 8 8-3.59 8-8 8zm3.5-9h-3V8.5h-1V11h-3v1h3v3.5h1V12h3v-1z"/>
                        </svg>
                      </div>
                      <h4>🏥 Nearest Hospitals</h4>
                    </div>
                    <div className="facility-content">
                      {hospitals.nearest_hospitals && (
                        <a
                          href={hospitals.nearest_hospitals.google_maps}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="facility-link"
                        >
                          <p className="facility-search-text">{hospitals.nearest_hospitals.display_text}</p>
                          <span className="facility-arrow">View Nearby →</span>
                        </a>
                      )}
                    </div>
                  </div>

                  <div className="facility-section">
                    <div className="facility-section-header">
                      <div className="facility-icon-bg clinic-bg">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M20 6h-2.18c.11-.89.36-1.75.72-2.54C19.07 2.18 18.56 1 17.5 1c-.96 0-1.46 1.18-1.38 2.46.36.79.61 1.65.72 2.54H6.94c.11-.89.36-1.75.72-2.54C8.07 2.18 7.56 1 6.5 1c-.96 0-1.46 1.18-1.38 2.46.36.79.61 1.65.72 2.54H4c-1.1 0-1.99.9-1.99 2v14c0 1.1.89 2 2 2h16c1.1 0 2-.9 2-2V8c0-1.1-.9-2-2-2zm0 16H4V8h16v14zm-5.04-6.71l-2.75 3.54-1.96-2.36c-.5-.6-1.45-.59-2.04.01-.59.6-.58 1.55.01 2.04l2.5 3c.29.35.75.56 1.25.56s.96-.21 1.25-.56l3.54-4.29c.59-.6.58-1.54-.01-2.04-.6-.59-1.56-.58-2.15.01z"/>
                        </svg>
                      </div>
                      <h4>🏢 Nearest Clinics</h4>
                    </div>
                    <div className="facility-content">
                      {hospitals.nearest_clinics && (
                        <a
                          href={hospitals.nearest_clinics.google_maps}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="facility-link"
                        >
                          <p className="facility-search-text">{hospitals.nearest_clinics.display_text}</p>
                          <span className="facility-arrow">View Nearby →</span>
                        </a>
                      )}
                    </div>
                  </div>

                  <div className="facility-section">
                    <div className="facility-section-header">
                      <div className="facility-icon-bg nursing-bg">
                        <svg width="32" height="32" viewBox="0 0 24 24" fill="currentColor">
                          <path d="M19 3H5c-1.1 0-2 .9-2 2v14c0 1.1.9 2 2 2h14c1.1 0 2-.9 2-2V5c0-1.1-.9-2-2-2zM9 17H7v-7h2v7zm4 0h-2V7h2v10zm4 0h-2v-4h2v4z"/>
                        </svg>
                      </div>
                      <h4>🏘️ Nursing Homes</h4>
                    </div>
                    <div className="facility-content">
                      {hospitals.nearest_nursing && (
                        <a
                          href={hospitals.nearest_nursing.google_maps}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="facility-link"
                        >
                          <p className="facility-search-text">{hospitals.nearest_nursing.display_text}</p>
                          <span className="facility-arrow">View Nearby →</span>
                        </a>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Diagnostic Conversation */}
        <div className="detail-card">
          <div className="card-header">
            <h2 className="card-title">Diagnostic Conversation</h2>
            <span className="card-count">{chatHistory.length} messages</span>
          </div>
          
          <div className="conversation-container">
            {chatHistory && chatHistory.length > 0 ? (
              chatHistory.map((msg, idx) => (
                <div key={idx} className="conversation-item">
                  {msg.human && (
                    <div className="conversation-msg user">
                      <div className="msg-header">
                        <span className="msg-sender">Patient</span>
                        <span className="msg-number">#{idx + 1}</span>
                      </div>
                      <p className="msg-text">{msg.human}</p>
                    </div>
                  )}
                  {msg.ai && (
                    <div className="conversation-msg ai">
                      <div className="msg-header">
                        <span className="msg-sender">
                          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                            <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" strokeWidth="2"/>
                          </svg>
                          MedSage AI
                        </span>
                      </div>
                      <div 
                        className="msg-text"
                        dangerouslySetInnerHTML={{ 
                          __html: msg.ai.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>').replace(/\n/g, '<br/>') 
                        }} 
                      />
                    </div>
                  )}
                </div>
              ))
            ) : (
              <div className="empty-conversation">
                <p>No conversation data found</p>
              </div>
            )}
          </div>
        </div>

        {/* Error Banner */}
        {error && (
          <div className="error-banner">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <circle cx="12" cy="12" r="10" strokeWidth="2"/>
              <line x1="12" y1="8" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
              <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth="2" strokeLinecap="round"/>
            </svg>
            <p>{error}</p>
            <button onClick={() => setError(null)} className="error-close">✕</button>
          </div>
        )}

        {/* Actions */}
        <div className="summary-actions">
          <button
            onClick={handleDownloadPDF}
            disabled={downloading}
            className="download-btn"
          >
            {downloading ? (
              <>
                <div className="btn-spinner"></div>
                <span>Generating PDF...</span>
              </>
            ) : (
              <>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                  <path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <polyline points="7 10 12 15 17 10" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  <line x1="12" y1="15" x2="12" y2="3" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                </svg>
                <span>Download PDF Report</span>
              </>
            )}
          </button>

          <button
            onClick={handleNewDiagnosis}
            className="home-btn"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <polyline points="9 22 9 12 15 12 15 22" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
            <span>New Diagnosis</span>
          </button>
        </div>
      </div>
    </div>
  );
}
