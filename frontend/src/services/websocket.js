let socket = null;

const WS_URL = import.meta.env.VITE_WS_URL || "ws://localhost:8000";

export const connectWebSocket = (diagramaId, token, onMessage, onOpen, onClose) => {
  // 🔹 Reusar socket existente si está abierto
  if (socket && socket.readyState === WebSocket.OPEN) {
    console.log("Ya hay conexión activa, reutilizando socket");
    return socket;
  }

  // 🔹 Construir URL con token
  const url = `${WS_URL}/ws/diagrama/${diagramaId}/?token=${encodeURIComponent(token)}`;
  console.log("Conectando WebSocket a:", url);
  socket = new WebSocket(url);

  socket.onopen = (event) => {
    console.log("WebSocket abierto", event);
    if (onOpen) onOpen(event);
  };

  socket.onmessage = (event) => {
    try {
      const data = JSON.parse(event.data);
      if (onMessage) onMessage(data);
    } catch (err) {
      console.error("Error parseando mensaje WebSocket:", err);
    }
  };

// En tu websocket.js
  socket.onclose = (event) => {
    console.log(`WebSocket cerrado para diagrama ${diagramaId}`, event);
    if (onClose) onClose(event);

  // 🔹 Redirigir si la conexión se perdió inesperadamente
    if (event.code !== 1000) { // 1000 = cierre normal
      window.location.href = "/dashboard";
    }
  };


  socket.onerror = (event) => {
    console.error("WebSocket error", event);
  };

  return socket;
};

// 🔹 Enviar mensaje al socket abierto
export const sendMessage = (message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.warn("No hay conexión WebSocket abierta");
  }
};

// 🔹 Cerrar la conexión manualmente
export const closeWebSocket = () => {
  if (socket) {
    socket.close();
    socket = null;
  }
};
