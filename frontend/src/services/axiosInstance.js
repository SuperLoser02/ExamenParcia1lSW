import axios from "axios";

const API_URL = import.meta.env.VITE_API_URL || "http://localhost:8000";

// Creamos una instancia de Axios
const axiosInstance = axios.create({
  baseURL: `${API_URL}/api/`,
  headers: {
    "Content-Type": "application/json",
  },
});

// Interceptor para agregar token a cada petición
axiosInstance.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("access_token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Interceptor para refrescar token si expira
axiosInstance.interceptors.response.use(
  (response) => response,
  async (error) => {
    const originalRequest = error.config;

    // Si es un 401 y tenemos refresh token
    if (
      error.response &&
      error.response.status === 401 &&
      !originalRequest._retry
    ) {
      originalRequest._retry = true;
      const refreshToken = localStorage.getItem("refresh_token");

      if (refreshToken) {
        try {
          const res = await axios.post(`${API_URL}/api/token/refresh/`, {
            refresh: refreshToken,
          });
          localStorage.setItem("access_token", res.data.access);

          // Reintenta la petición original
          originalRequest.headers.Authorization = `Bearer ${res.data.access}`;
          return axiosInstance(originalRequest);
        } catch (err) {
          // Si falla el refresh, cerramos sesión
          localStorage.removeItem("access_token");
          localStorage.removeItem("refresh_token");
          window.location.href = "/";
          return Promise.reject(err);
        }
      } else {
        window.location.href = "/";
      }
    }
    return Promise.reject(error);
  }
);

export default axiosInstance;
