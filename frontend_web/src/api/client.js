import axios from "axios";

const api = axios.create({
  baseURL: "http://127.0.0.1:8000",
});

// Ajouter automatiquement le token
api.interceptors.request.use((config) => {
  const token = localStorage.getItem("token"); // ou sessionStorage
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

export default api;
