import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";

export default function PatientInfo() {
  const navigate = useNavigate();

  // State to hold form data for patient info
  const [formData, setFormData] = useState({
    name: "",
    dob: "",
    gender: "",
    symptoms: ""
  });

  // State to hold validation errors
  const [errors, setErrors] = useState({});

  // State to trigger slide-up animation on mount
  const [isAnimated, setIsAnimated] = useState(false);

  // Trigger animation on component mount
  useEffect(() => {
    setIsAnimated(true);
  }, []);

  // Update form data and clear errors on input change
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
    if (errors[name]) {
      setErrors(prev => ({ ...prev, [name]: "" }));
    }
  };

  // Basic form validation
  const validateForm = () => {
    const newErrors = {};
    if (!formData.name.trim()) newErrors.name = "Name is required";
    if (!formData.dob) newErrors.dob = "Date of birth is required";
    if (!formData.gender) newErrors.gender = "Please select gender";
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  // On form submit, validate data, calculate age, save and navigate
  const handleSubmit = (e) => {
    e.preventDefault();
    if (!validateForm()) return;

    const age = new Date().getFullYear() - new Date(formData.dob).getFullYear();
    const dataWithAge = { ...formData, age };

    sessionStorage.setItem("patientDetails", JSON.stringify(dataWithAge));
    navigate("/chat");
  };

  return (
    <div className="patient-info-page">
      <div className="bg-decoration"></div>

      <div className={`patient-form-wrapper ${isAnimated ? 'slide-up' : ''}`}>
        {/* Form header with back navigation */}
        <div className="form-header">
          <button 
            onClick={() => navigate("/")} 
            className="back-button"
            aria-label="Go back to home"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M19 12H5M12 19l-7-7 7-7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
          <h2 className="form-title">Patient Information</h2>
          <p className="form-subtitle">Please provide accurate details for diagnosis</p>
        </div>

        {/* Progress steps */}
        <div className="progress-steps">
          <div className="step active">
            <div className="step-number">1</div>
            <span>Patient Info</span>
          </div>
          <div className="step-line"></div>
          <div className="step">
            <div className="step-number">2</div>
            <span>Diagnosis</span>
          </div>
          <div className="step-line"></div>
          <div className="step">
            <div className="step-number">3</div>
            <span>Summary</span>
          </div>
        </div>

        {/* Patient details form */}
        <form onSubmit={handleSubmit} className="patient-form">
          {/* Name input */}
          <div className="form-group">
            <label htmlFor="name" className="form-label">
              <span className="label-icon">👤</span>
              Full Name
              <span className="required">*</span>
            </label>
            <input
              type="text"
              id="name"
              name="name"
              value={formData.name}
              onChange={handleChange}
              className={`form-input ${errors.name ? 'error' : ''}`}
              placeholder="Enter patient's full name"
              aria-required="true"
            />
            {errors.name && <span className="error-message">{errors.name}</span>}
          </div>

          {/* Date of Birth input */}
          <div className="form-group">
            <label htmlFor="dob" className="form-label">
              <span className="label-icon">📅</span>
              Date of Birth
              <span className="required">*</span>
            </label>
            <input
              type="date"
              id="dob"
              name="dob"
              value={formData.dob}
              onChange={handleChange}
              max={new Date().toISOString().split('T')[0]}
              className={`form-input ${errors.dob ? 'error' : ''}`}
              aria-required="true"
            />
            {errors.dob && <span className="error-message">{errors.dob}</span>}
          </div>

          {/* Gender select */}
          <div className="form-group">
            <label htmlFor="gender" className="form-label">
              <span className="label-icon">⚤</span>
              Gender
              <span className="required">*</span>
            </label>
            <select
              id="gender"
              name="gender"
              value={formData.gender}
              onChange={handleChange}
              className={`form-input ${errors.gender ? 'error' : ''}`}
              aria-required="true"
            >
              <option value="">Select Gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
            {errors.gender && <span className="error-message">{errors.gender}</span>}
          </div>

          {/* Optional symptoms textarea */}
          <div className="form-group">
            <label htmlFor="symptoms" className="form-label">
              <span className="label-icon">💬</span>
              Primary Symptoms (Optional)
            </label>
            <textarea
              id="symptoms"
              name="symptoms"
              value={formData.symptoms}
              onChange={handleChange}
              className="form-input"
              placeholder="Brief description of main symptoms..."
              rows="3"
            />
          </div>

          {/* Submit button */}
          <button type="submit" className="submit-button">
            <span>Continue to Diagnosis</span>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor">
              <path d="M5 12h14M12 5l7 7-7 7" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
            </svg>
          </button>
        </form>

        {/* Privacy notice below form */}
        <div className="privacy-notice">
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"/>
          </svg>
          <span>Remember: Providing detailed and honest information helps us give you the most accurate health guidance.</span>
        </div>
      </div>
    </div>
  );
}
