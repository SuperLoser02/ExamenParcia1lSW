import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";
import styles from "../styles/authStyles";

export default function Recover() {
  const [email, setEmail] = useState("");
  const [message, setMessage] = useState("");
  const navigate = useNavigate();

  const handleRecover = async (e) => {
    e.preventDefault();
    try {
      await axiosInstance.post("recover/", { email });
      setMessage("Se envió un email con instrucciones");
    } catch (err) {
      setMessage("Error al enviar el email");
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

        <h1 style={styles.title}>Recuperar Contraseña</h1>
        <form onSubmit={handleRecover} style={styles.form}>
          <input
            style={styles.input}
            placeholder="Email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
          />
          <button style={styles.button} type="submit">
            Enviar
          </button>
        </form>
        {message && <p style={{ marginTop: "10px" }}>{message}</p>}
      </div>
    </div>
  );
}
