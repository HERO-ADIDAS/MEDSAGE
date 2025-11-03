import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import "../utils/App.css";

const PatientForm = () => {
  const navigate = useNavigate();

  // State to hold patient details form inputs
  const [patient, setPatient] = useState({
    name: "",
    dob: "",
    age: "",
    gender: "",
  });

  // Generic handler for form input changes
  const handleChange = (e) => {
    const { name, value } = e.target;
    setPatient({ ...patient, [name]: value });
  };

  // Form submission handler: saves patient info and navigates to chat page
  const handleSubmit = (e) => {
    e.preventDefault();
    localStorage.setItem("patientInfo", JSON.stringify(patient));
    navigate("/chat");
  };

  return (
    /* Container with centered form */
    <div className="patient-form-container flex justify-center items-center min-h-screen bg-gray-50">
      <div className="bg-white p-8 rounded-2xl shadow-md w-full max-w-md">
        <h1 className="text-2xl font-semibold text-center mb-6 text-blue-600">
          Enter Patient Information
        </h1>
        <form onSubmit={handleSubmit} className="space-y-4">
          {/* Name input */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Full Name</label>
            <input
              type="text"
              name="name"
              value={patient.name}
              onChange={handleChange}
              placeholder="Enter full name"
              required
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {/* Date of Birth input */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Date of Birth</label>
            <input
              type="date"
              name="dob"
              value={patient.dob}
              onChange={handleChange}
              required
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {/* Age input */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Age</label>
            <input
              type="number"
              name="age"
              value={patient.age}
              onChange={handleChange}
              placeholder="Enter age"
              required
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-400"
            />
          </div>

          {/* Gender select */}
          <div>
            <label className="block text-gray-700 font-medium mb-1">Gender</label>
            <select
              name="gender"
              value={patient.gender}
              onChange={handleChange}
              required
              className="w-full border rounded-lg p-2 focus:ring-2 focus:ring-blue-400"
            >
              <option value="">Select gender</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
              <option value="Other">Other</option>
            </select>
          </div>

          {/* Submit button */}
          <button
            type="submit"
            className="w-full bg-blue-600 text-white py-2 rounded-lg hover:bg-blue-700 transition"
          >
            Proceed to Diagnosis
          </button>
        </form>
      </div>
    </div>
  );
};

export default PatientForm;
