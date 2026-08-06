import axios from "axios";

const API_URL = process.env.REACT_APP_API_URL || "http://127.0.0.1:8000";

const client = axios.create({ baseURL: API_URL });

// Attach the stored token to every request automatically
client.interceptors.request.use((config) => {
  const token = localStorage.getItem("token");
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Normalize FastAPI error responses into a plain string
client.interceptors.response.use(
  (res) => res,
  (err) => {
    const detail = err?.response?.data?.detail;
    const message = Array.isArray(detail)
      ? detail.map((d) => d.msg).join(", ")
      : detail || "Something went wrong. Please try again.";
    return Promise.reject(new Error(message));
  }
);

// ---------------------------------------------------------
// Auth
// ---------------------------------------------------------

export const registerUser = (data) => client.post("/auth/register", data);
export const loginUser = (data) => client.post("/auth/login", data);

// ---------------------------------------------------------
// Athletes
// ---------------------------------------------------------

export const listAthletes = () => client.get("/athletes");
export const getAthlete = (id) => client.get(`/athletes/${id}`);
export const createAthlete = (data) => client.post("/athletes", data);
export const updateAthlete = (id, data) => client.put(`/athletes/${id}`, data);
export const deleteAthlete = (id) => client.delete(`/athletes/${id}`);

// ---------------------------------------------------------
// Videos & biomechanical analysis (Milestone 2)
// ---------------------------------------------------------

export const listVideos = (athleteId) => client.get(`/athletes/${athleteId}/videos`);

export const uploadVideo = (athleteId, file) => {
  const formData = new FormData();
  formData.append("file", file);
  return client.post(`/athletes/${athleteId}/videos`, formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
};

export const analyzeVideo = (videoId) => client.post(`/videos/${videoId}/analyze`);
export const getReport = (videoId) => client.get(`/videos/${videoId}/report`);

// ---------------------------------------------------------
// Injury risk prediction, anomaly detection & recommendations (Milestone 3)
// ---------------------------------------------------------

export const getRiskAssessment = (videoId) => client.get(`/videos/${videoId}/risk-assessment`);
export const getRiskTrend = (athleteId) => client.get(`/athletes/${athleteId}/risk-trend`);

export default client;
