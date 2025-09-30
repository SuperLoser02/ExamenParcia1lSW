const pizarraStyles = {
  // Contenedor principal
  container: {
    height: "100vh",
    display: "flex",
    flexDirection: "column",
    backgroundColor: "#f8fafc",
    overflow: "hidden"
  },

  // Header
  header: {
    height: "60px",
    backgroundColor: "#ffffff",
    borderBottom: "1px solid #e5e7eb",
    display: "flex",
    alignItems: "center",
    justifyContent: "space-between",
    padding: "0 20px",
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
    zIndex: 100
  },

  headerTitle: {
    margin: 0,
    fontSize: "20px",
    fontWeight: "600",
    color: "#1f2937"
  },

  btnCerrarSesion: {
    backgroundColor: "#ef4444",
    color: "white",
    border: "none",
    padding: "8px 16px",
    borderRadius: "6px",
    cursor: "pointer",
    fontWeight: "500",
    fontSize: "14px"
  },

  // Layout principal
  mainLayout: {
    display: "flex",
    flex: 1,
    overflow: "hidden",
    position: "relative"
  },

  // Sidebar
  sidebar: {
    width: "240px",
    backgroundColor: "#ffffff",
    borderRight: "1px solid #e5e7eb",
    padding: "20px",
    boxShadow: "1px 0 3px 0 rgba(0, 0, 0, 0.1)",
    overflowY: "auto",
    transition: "transform 0.3s ease"
  },

  sidebarTitle: {
    margin: "0 0 20px 0",
    fontSize: "16px",
    fontWeight: "600",
    color: "#1f2937"
  },

  herramientasContainer: {
    display: "flex",
    flexDirection: "column",
    gap: "12px"
  },

  // Botones de herramientas
  btnHerramienta: {
    padding: "12px",
    border: "1px solid #d1d5db",
    borderRadius: "8px",
    backgroundColor: "transparent",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    gap: "8px",
    fontWeight: "500",
    fontSize: "14px",
    transition: "all 0.2s",
    textAlign: "left"
  },

  btnHerramientaActiva: {
    border: "2px solid #3b82f6",
    backgroundColor: "#eff6ff"
  },

  // Iconos de herramientas
  iconoTabla: {
    width: "20px",
    height: "20px",
    backgroundColor: "#3b82f6",
    borderRadius: "2px"
  },

  iconoHerencia: {
    width: "20px",
    height: "2px",
    backgroundColor: "#10b981",
    position: "relative"
  },

  flechaHerencia: {
    position: "absolute",
    right: "0",
    top: "-3px",
    width: "0",
    height: "0",
    borderLeft: "6px solid #10b981",
    borderTop: "4px solid transparent",
    borderBottom: "4px solid transparent"
  },

  iconoAsociacion: {
    width: "20px",
    height: "2px",
    backgroundColor: "#3b82f6"
  },

  iconoComposicion: {
    width: "8px",
    height: "8px",
    backgroundColor: "#ef4444",
    transform: "rotate(45deg)",
    marginRight: "4px"
  },

  iconoAgregacion: {
    width: "8px",
    height: "8px",
    border: "2px solid #f59e0b",
    transform: "rotate(45deg)",
    backgroundColor: "transparent",
    marginRight: "4px"
  },

  // Información de herramienta
  infoHerramienta: {
    marginTop: "20px",
    padding: "12px",
    backgroundColor: "#f3f4f6",
    borderRadius: "6px",
    fontSize: "14px",
    color: "#4b5563",
    lineHeight: "1.5"
  },

  infoRelacionProgreso: {
    marginTop: "12px",
    padding: "8px",
    backgroundColor: "#dbeafe",
    borderRadius: "6px",
    fontSize: "12px",
    color: "#1e40af",
    lineHeight: "1.4"
  },

  // Toggle sidebar
  btnToggleSidebar: {
    position: "absolute",
    left: "240px",
    top: "80px",
    zIndex: 1000,
    width: "30px",
    height: "30px",
    backgroundColor: "#ffffff",
    border: "1px solid #d1d5db",
    borderRadius: "0 6px 6px 0",
    cursor: "pointer",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
    transition: "left 0.3s ease"
  },

  btnToggleSidebarClosed: {
    left: "0px"
  },

  iconoMenuBurger: {
    display: "flex",
    flexDirection: "column",
    gap: "2px"
  },

  lineaMenuBurger: {
    width: "12px",
    height: "2px",
    backgroundColor: "#6b7280",
    borderRadius: "1px"
  },

  // Área de pizarra (Stage)
  pizarraContainer: {
    flex: 1,
    position: "relative",
    overflow: "hidden",
    backgroundColor: "#ffffff"
  },

  // Modales
  modalOverlay: {
    position: "fixed",
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: "rgba(0, 0, 0, 0.5)",
    display: "flex",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 2000
  },

  modal: {
    backgroundColor: "white",
    padding: "30px",
    borderRadius: "12px",
    boxShadow: "0 20px 25px -5px rgba(0, 0, 0, 0.1)",
    width: "400px",
    maxHeight: "80vh",
    overflowY: "auto"
  },

  modalLarge: {
    width: "600px"
  },

  modalTitle: {
    margin: "0 0 20px 0",
    fontSize: "18px",
    fontWeight: "600",
    color: "#1f2937"
  },

  // Inputs
  input: {
    width: "100%",
    padding: "12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "16px",
    marginBottom: "20px",
    boxSizing: "border-box"
  },

  select: {
    width: "100%",
    padding: "12px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    fontSize: "14px",
    marginBottom: "12px",
    boxSizing: "border-box",
    backgroundColor: "white"
  },

  label: {
    display: "block",
    marginBottom: "6px",
    fontSize: "14px",
    fontWeight: "500",
    color: "#374151"
  },

  checkbox: {
    width: "16px",
    height: "16px",
    cursor: "pointer"
  },

  checkboxContainer: {
    display: "flex",
    alignItems: "center",
    gap: "8px",
    marginBottom: "12px"
  },

  // Botones
  btnPrimary: {
    padding: "10px 20px",
    border: "none",
    borderRadius: "6px",
    backgroundColor: "#3b82f6",
    color: "white",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500"
  },

  btnSecondary: {
    padding: "10px 20px",
    border: "1px solid #d1d5db",
    borderRadius: "6px",
    backgroundColor: "transparent",
    cursor: "pointer",
    fontSize: "14px",
    color: "#374151"
  },

  btnSuccess: {
    padding: "10px 20px",
    border: "none",
    borderRadius: "6px",
    backgroundColor: "#10b981",
    color: "white",
    cursor: "pointer",
    fontSize: "14px",
    fontWeight: "500"
  },

  btnDanger: {
    padding: "4px 8px",
    backgroundColor: "#ef4444",
    color: "white",
    border: "none",
    borderRadius: "4px",
    cursor: "pointer",
    fontSize: "12px"
  },

  btnDisabled: {
    backgroundColor: "#9ca3af",
    cursor: "not-allowed"
  },

  // Contenedores de botones
  btnGroup: {
    display: "flex",
    gap: "10px",
    justifyContent: "flex-end",
    marginTop: "20px"
  },

  btnGroupSpaceBetween: {
    display: "flex",
    gap: "10px",
    justifyContent: "space-between",
    marginTop: "20px"
  },

  // Lista de atributos
  atributoItem: {
    display: "flex",
    justifyContent: "space-between",
    alignItems: "center",
    padding: "10px",
    border: "1px solid #e5e7eb",
    borderRadius: "6px",
    marginBottom: "8px"
  },

  atributoInfo: {
    display: "flex",
    flexDirection: "column",
    gap: "4px"
  },

  atributoNombre: {
    fontWeight: "600",
    fontSize: "14px",
    color: "#1f2937"
  },

  atributoDetalle: {
    fontSize: "12px",
    color: "#6b7280"
  },

  badgePK: {
    display: "inline-block",
    backgroundColor: "#fee2e2",
    color: "#dc2626",
    padding: "2px 6px",
    borderRadius: "4px",
    fontSize: "11px",
    fontWeight: "600",
    marginLeft: "6px"
  },

  badgeNull: {
    display: "inline-block",
    backgroundColor: "#f3f4f6",
    color: "#6b7280",
    padding: "2px 6px",
    borderRadius: "4px",
    fontSize: "11px",
    marginLeft: "6px"
  },

  // Form grid
  formRow: {
    display: "grid",
    gridTemplateColumns: "1fr 1fr",
    gap: "12px",
    marginBottom: "12px"
  },

  formGroup: {
    marginBottom: "16px"
  },

  // Empty state
  emptyState: {
    padding: "20px",
    textAlign: "center",
    color: "#9ca3af",
    fontSize: "14px",
    fontStyle: "italic"
  }
};

export default pizarraStyles;