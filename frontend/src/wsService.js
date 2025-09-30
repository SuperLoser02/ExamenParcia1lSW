let socket = null;

export const connectWebSocket = () => {
  socket = new WebSocket("ws://localhost:8000/ws/diagrama/"); 
  // 👆 ajusta la URL si tu backend corre en otra ruta

  socket.onopen = () => {
    console.log("✅ Conectado al WebSocket");
  };

  socket.onmessage = (event) => {
    console.log("📩 Mensaje recibido:", event.data);
  };

  socket.onclose = () => {
    console.log("❌ WebSocket cerrado");
  };

  socket.onerror = (error) => {
    console.error("⚠️ Error en WebSocket:", error);
  };
};

export const sendMessage = (message) => {
  if (socket && socket.readyState === WebSocket.OPEN) {
    socket.send(JSON.stringify(message));
  } else {
    console.error("WebSocket no está abierto");
  }
};
