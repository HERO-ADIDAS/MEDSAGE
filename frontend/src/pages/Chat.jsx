import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import ChatBox from "../components/ChatBox";

const Chat = () => {
  // State hooks for chat history, loading status, patient data and error message
  const [chatHistory, setChatHistory] = useState([]);
  const [loading, setLoading] = useState(false);
  const [patientData, setPatientData] = useState(null);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // On mount, load patient details from sessionStorage and handle errors or redirection
  useEffect(() => {
    const stored = sessionStorage.getItem("patientDetails");

    if (!stored) {
      setError("Please enter patient information first");
      // Redirect after 2 seconds to patient info form
      setTimeout(() => navigate("/patient-info"), 2000);
      return;
    }

    try {
      const parsedData = JSON.parse(stored);
      setPatientData(parsedData);
    } catch (err) {
      console.error("Failed to parse patient data:", err);
      setError("Invalid patient data");
      setTimeout(() => navigate("/patient-info"), 2000);
    }
  }, [navigate]);

  // Show error UI if error exists
  if (error) {
    return (
      <div className="error-container">
        <div className="error-card">
          <svg width="64" height="64" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <circle cx="12" cy="12" r="10" strokeWidth="2"/>
            <line x1="12" y1="8" x2="12" y2="12" strokeWidth="2" strokeLinecap="round"/>
            <line x1="12" y1="16" x2="12.01" y2="16" strokeWidth="2" strokeLinecap="round"/>
          </svg>
          <h2>{error}</h2>
          <p>Redirecting to patient information form...</p>
        </div>
      </div>
    );
  }

  // Show loading placeholder if patient data not yet loaded
  if (!patientData) {
    return (
      <div className="loading-container">
        <div className="spinner"></div>
        <p>Loading patient information...</p>
      </div>
    );
  }

  // Render ChatBox with relevant props once patient data is ready
  return (
    <div className="chat-wrapper">
      <ChatBox
        patientData={patientData}
        chatHistory={chatHistory}
        setChatHistory={setChatHistory}
        loading={loading}
        setLoading={setLoading}
      />
    </div>
  );
};

export default Chat;
