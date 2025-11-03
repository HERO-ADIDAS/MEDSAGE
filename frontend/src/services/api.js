// src/services/api.js
import axios from "axios";

const API_BASE_URL = "http://127.0.0.1:8000/api";

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    "Content-Type": "application/json",
  },
});

export const submitPatientInfo = async (patientData) => {
  try {
    const response = await apiClient.post("/patient", patientData);
    return response.data;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};

export const sendChat = async (query, history) => {
  try {
    const response = await apiClient.post("/chat", {
      query: query,
      history: history,
    });
    return response.data;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};

export const generatePDF = async (userDetails, chatHistory) => {
  try {
    const response = await apiClient.post("/generate_report", {
      user_details: userDetails,
      chat_history: chatHistory,
    }, {
      responseType: "blob",
    });
    return response;
  } catch (error) {
    console.error("Error:", error);
    throw error;
  }
};

// ✅ Extract specialist from chat history
export const extractSpecialist = async (chatHistory) => {
  try {
    const response = await apiClient.post("/extract_specialist", {
      chat_history: chatHistory
    });
    return response.data;
  } catch (error) {
    console.error("Error extracting specialist:", error);
    throw error;
  }
};

// Get Nearest Facilities
export const getNearestFacilities = async (pincode, specialist = "", facilityType = "all") => {
  try {
    const response = await apiClient.post("/get_nearest_facilities", {
      pincode: pincode,
      specialist: specialist,
      facility_type: facilityType
    });
    return response.data;
  } catch (error) {
    console.error("Error:", error);
    if (error.response?.data?.detail) {
      throw new Error(error.response.data.detail);
    }
    throw error;
  }
};
