import axios from "axios";

const API_URL = "http://127.0.0.1:8000";

export const register = (data) => axios.post(`${API_URL}/auth/register`, data);
export const login = (data) => axios.post(`${API_URL}/auth/login`, data);

export const createAthlete = (data, token) =>
  axios.post(`${API_URL}/athletes`, data, {
    headers: { Authorization: `Bearer ${token}` },
  });

export const listAthletes = (token) =>
  axios.get(`${API_URL}/athletes`, {
    headers: { Authorization: `Bearer ${token}` },
  });