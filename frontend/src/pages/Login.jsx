import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";
import styles from "../styles/authStyles";


export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const navigate = useNavigate();

  // Si ya hay token, redirige automáticamente al dashboard
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (token) {
      navigate("/dashboard");
    }
  }, [navigate]);

  const handleLogin = async (e) => {
    e.preventDefault();
    setError(""); // limpiar error previo
    try {
      const response = await axiosInstance.post("token/", {
        username,
        password,
      });

      // Guardar tokens
      localStorage.setItem("access_token", response.data.access);
      localStorage.setItem("refresh_token", response.data.refresh);

      // Redirigir a dashboard
      navigate("/dashboard");
    } catch (err) {
      // Manejo de errores del backend
      if (err.response && err.response.status === 401) {
        setError("Usuario o contraseña incorrectos");
      } else {
        setError("Ocurrió un error inesperado");
      }
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.box}>
        <h1 style={styles.title}>Iniciar Sesión</h1>
        <form onSubmit={handleLogin} style={styles.form}>
          <input
            style={styles.input}
            type="text"
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            style={styles.input}
            type="password"
            placeholder="Contraseña"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button type="submit" style={styles.button}>Ingresar</button>
        </form>
        {error && <p style={styles.error}>{error}</p>}
        <div style={{ textAlign: "center", marginTop: "15px" }}>
            <button
                style={styles.linkButton}
                onClick={() => navigate("/register")}
            >
                Crear usuario
            </button>
            {/*<button
                style={styles.linkButton}
                onClick={() => navigate("/recover")}
            >
                ¿Olvidaste tu contraseña?
            </button>*/}
        </div>
      </div>
    </div>
  );
}

