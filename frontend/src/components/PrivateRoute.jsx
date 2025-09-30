import { Navigate } from "react-router-dom";

export default function PrivateRoute({ children }) {
  const token = localStorage.getItem("access_token");

  if (!token) {
    // Si no hay token, redirige al login
    return <Navigate to="/" replace />;
  }

  // Si hay token, muestra la ruta
  return children;
}
