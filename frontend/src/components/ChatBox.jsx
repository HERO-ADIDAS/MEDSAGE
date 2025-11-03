import React, { useState, useRef, useEffect } from "react";
import { sendChat } from "../services/api";
import { useNavigate } from "react-router-dom";

const ChatBox = ({ patientData, chatHistory, setChatHistory, loading, setLoading }) => {
  // Local state for user input and error display
  const [query, setQuery] = useState("");
  const [error, setError] = useState(null);
  // Detect if diagnosis conversation is complete
  const [diagnosisComplete, setDiagnosisComplete] = useState(false);
  const chatEndRef = useRef(null);
  const navigate = useNavigate();

  // Scroll to bottom on new chat history
  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [chatHistory]);

  // Persist chat history to sessionStorage on update
  useEffect(() => {
    if (chatHistory.length > 0) {
      sessionStorage.setItem("chatHistory", JSON.stringify(chatHistory));
    }
  }, [chatHistory]);

  // Restore chat history from sessionStorage on mount
  useEffect(() => {
    const saved = sessionStorage.getItem("chatHistory");
    if (saved && chatHistory.length === 0) {
      try {
        setChatHistory(JSON.parse(saved));
      } catch (err) {
        console.warn("Failed to restore chat history:", err);
      }
    }
  }, []);

  // Check AI response if diagnosis is complete based on keywords
  const checkDiagnosisComplete = (aiResponse) => {
    const diagnosisKeywords = [
      "final diagnosis",
      "final assessment",
      "most likely diagnosis",
      "diagnosis is",
      "recommended specialist",
      "self-care advice",
      "severity level"
    ];

    const lowerResponse = aiResponse.toLowerCase();
    const isComplete = diagnosisKeywords.some(keyword => lowerResponse.includes(keyword));
    
    if (isComplete) {
      console.log("✅ Diagnosis complete detected!");
      setDiagnosisComplete(true);
    }
    
    return isComplete;
  };

  // Format message text with simple markdown replacements
  const formatMessage = (text) => {
    if (!text) return "";
    return text
      .replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>')
      .replace(/\*([^*]+)\*/g, '<em>$1</em>')
      .replace(/\n/g, '<br/>');
  };

  // Handle sending the user query to backend and processing response
  const handleSend = async () => {
    if (!query.trim() || loading) return;

    setError(null);
    setLoading(true);
    
    const userQuery = query.trim();
    const userMessage = { human: userQuery, ai: "" };
    
    setChatHistory([...chatHistory, userMessage]);
    setQuery("");

    try {
      const response = await sendChat(userQuery, chatHistory);

      if (response?.ai_response) {
        checkDiagnosisComplete(response.ai_response);
        
        setChatHistory(prev => {
          const updated = [...prev];
          updated[updated.length - 1] = {
            human: userQuery,
            ai: response.ai_response
          };
          return updated;
        });
      } else {
        throw new Error("No AI response received");
      }
    } catch (err) {
      console.error("Chat error:", err);
      setError(err.response?.data?.detail || "Failed to get response. Please try again.");
      setChatHistory(prev => prev.slice(0, -1));  // Remove last user message on error
    } finally {
      setLoading(false);
    }
  };

  // Support submitting message on Enter key without shift
  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  // Navigate to summary page with current patient and chat data
  const handleProceedToSummary = () => {
    navigate("/summary", {
      state: {
        userDetails: patientData,
        chatHistory: chatHistory
      }
    });
  };

  // Clear all chat data with confirmation
  const handleClearChat = () => {
    if (window.confirm("Are you sure you want to clear the conversation?")) {
      setChatHistory([]);
      setDiagnosisComplete(false);
      sessionStorage.removeItem("chatHistory");
    }
  };

  return (
    <div className="chat-page">
      {/* Header with back and clear buttons */}
      <div className="chat-header">
        <div className="header-content">
          <button 
            onClick={() => navigate("/")} 
            className="header-back-btn"
            aria-label="Go home"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5M12 19l-7-7 7-7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          
          <div className="header-info">
            <h2 className="header-title">MedSage Diagnostic Chat</h2>
            {patientData && (
              <p className="header-patient">
                <span className="patient-icon">👤</span>
                {patientData.name} • {patientData.age} yrs • {patientData.gender}
              </p>
            )}
          </div>

          <button 
            onClick={handleClearChat}
            className="header-clear-btn"
            title="Clear conversation"
            disabled={chatHistory.length === 0}
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <polyline points="3 6 5 6 21 6" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"/>
            </svg>
          </button>
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

      {/* Chat Body */}
      <div className="chat-body">
        {chatHistory.length === 0 ? (
          <div className="chat-empty-state">
            <div className="empty-icon">💬</div>
            <h3>Start Your Diagnosis</h3>
            <p>Describe your symptoms in detail. The more information you provide, the better the diagnosis.</p>
            <div className="example-prompts">
              <p className="prompt-label">Example questions:</p>
              <button onClick={() => setQuery("I have a persistent headache and fever")} className="prompt-btn">
                "I have a persistent headache and fever"
              </button>
              <button onClick={() => setQuery("Experiencing chest pain when breathing")} className="prompt-btn">
                "Experiencing chest pain when breathing"
              </button>
            </div>
          </div>
        ) : (
          <>
            {chatHistory.map((msg, idx) => (
              <div key={idx} className="chat-msg-group">
                {/* User message */}
                {msg.human && (
                  <div className="msg user-msg">
                    <div className="msg-content">
                      <div className="msg-avatar user-avatar">
                        <span>You</span>
                      </div>
                      <div className="msg-bubble">
                        <p>{msg.human}</p>
                      </div>
                    </div>
                  </div>
                )}

                {/* AI message */}
                {msg.ai ? (
                  <div className="msg ai-msg">
                    <div className="msg-content">
                      <div className="msg-avatar ai-avatar">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                          <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" fill="currentColor"/>
                        </svg>
                      </div>
                      <div className="msg-bubble">
                        <div dangerouslySetInnerHTML={{ 
                          __html: formatMessage(msg.ai)
                        }} />
                      </div>
                    </div>
                  </div>
                ) : loading && idx === chatHistory.length - 1 ? (
                  <div className="msg ai-msg">
                    <div className="msg-content">
                      <div className="msg-avatar ai-avatar">
                        <svg width="24" height="24" viewBox="0 0 24 24" fill="none">
                          <path d="M12 2L2 7v10c0 5.55 3.84 10.74 9 12 5.16-1.26 9-6.45 9-12V7l-10-5z" fill="currentColor"/>
                        </svg>
                      </div>
                      <div className="msg-bubble thinking-bubble">
                        <span className="thinking-text">Analyzing</span>
                        <div className="dots">
                          <span></span>
                          <span></span>
                          <span></span>
                        </div>
                      </div>
                    </div>
                  </div>
                ) : null}
              </div>
            ))}
          </>
        )}
        <div ref={chatEndRef} />
      </div>

      {/* Footer with Input and Buttons */}
      <div className="chat-footer">
        <div className="input-container">
          <textarea
            className="chat-input"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder="Describe your symptoms in detail..."
            rows={2}
            disabled={loading}
            aria-label="Message input"
          />
          
          <div className="footer-actions">
            <button
              className="send-btn"
              onClick={handleSend}
              disabled={loading || !query.trim()}
              aria-label="Send message"
            >
              {loading ? (
                <>
                  <div className="btn-spinner"></div>
                  <span>Analyzing...</span>
                </>
              ) : (
                <>
                  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                    <line x1="22" y1="2" x2="11" y2="13" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                    <polygon points="22 2 15 22 11 13 2 9 22 2" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                  </svg>
                  <span>Send</span>
                </>
              )}
            </button>

            <button
              className={`summary-btn ${diagnosisComplete ? 'enabled' : 'disabled'}`}
              onClick={handleProceedToSummary}
              disabled={!diagnosisComplete || loading}
              title={diagnosisComplete ? "View diagnosis summary" : "Complete the diagnosis first"}
              aria-label="View summary"
            >
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
                <path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <polyline points="14 2 14 8 20 8" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <line x1="16" y1="13" x2="8" y2="13" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
                <line x1="16" y1="17" x2="8" y2="17" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
              </svg>
              <span>View Summary</span>
            </button>
          </div>
        </div>

        <p className="input-hint">
          Press <kbd>Enter</kbd> to send • <kbd>Shift + Enter</kbd> for new line
        </p>
      </div>
    </div>
  );
};

export default ChatBox;
