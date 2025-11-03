// src/services/storage.js
const STORAGE_KEY = "medsage_session";

export function saveSession(data) {
  localStorage.setItem(STORAGE_KEY, JSON.stringify(data));
}

export function loadSession() {
  const data = localStorage.getItem(STORAGE_KEY);
  return data ? JSON.parse(data) : null;
}

export function clearSession() {
  localStorage.removeItem(STORAGE_KEY);
}
