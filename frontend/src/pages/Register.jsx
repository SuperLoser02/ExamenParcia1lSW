import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";
import styles from "../styles/authStyles";

export default function Register() {
  const [firstName, setFirstName] = useState("");
  const [lastName, setLastName] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [email, setEmail] = useState("");
  const [error, setError] = useState("");
  const [success, setSuccess] = useState("");
  const navigate = useNavigate();

  const handleRegister = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("register/", {
        first_name: firstName,
        last_name: lastName,
        username,
        password,
        email,
      });
      setSuccess("Usuario creado exitosamente");
      setTimeout(() => navigate("/"), 1500);
    } catch (err) {
      setError("Error al crear el usuario");
    }
  };

  return (
    <div style={styles.container}>
      <div style={styles.box}>
        {/* Flecha para volver */}
        <button
          onClick={() => navigate("/")}
          style={styles.button}
        >
          ←
        </button>

        <h1 style={styles.title}>Crear Usuario</h1>
        <form onSubmit={handleRegister} style={styles.form}>
          <input
            style={styles.input}
            placeholder="Nombre"
            value={firstName}
            onChange={(e) => setFirstName(e.target.value)}
          />
          <input
            style={styles.input}
            placeholder="Apellido"
            value={lastName}
            onChange={(e) => setLastName(e.target.value)}
          />
          <input
            style={styles.input}
            placeholder="Usuario"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
          />
          <input
            style={styles.input}
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <input
            style={styles.input}
            placeholder="Contraseña"
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
          />
          <button style={styles.button} type="submit">
            Crear
          </button>
        </form>
        {error && <p style={styles.error}>{error}</p>}
        {success && <p style={{ color: "green", marginTop: "10px" }}>{success}</p>}
      </div>
    </div>
  );
}
