import { useEffect, useState, useRef } from "react";
import { useNavigate } from "react-router-dom";
import axiosInstance from "../services/axiosInstance";
import {
  getUltimosDiagramas,
  getMisDiagramas,
  getColaboraciones,
} from "../services/diagramaService";
import styles from "../styles/dashboardStyles";

export default function Dashboard() {
  const navigate = useNavigate();
  const [user, setUser] = useState(null);
  const [dropdownOpen, setDropdownOpen] = useState(false);
  const [ultimos, setUltimos] = useState([]);
  const [misDiagramas, setMisDiagramas] = useState([]);
  const [colaboraciones, setColaboraciones] = useState([]);
  const dropdownRef = useRef(null);

  // Crear Diagramas
  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDiagramaName, setNewDiagramaName] = useState("");
  const [createMessage, setCreateMessage] = useState("");
  const [creating, setCreating] = useState(false);

  // Invitar
  const [showInviteModal, setShowInviteModal] = useState(false);
  const [selectedDiagram, setSelectedDiagram] = useState(null);
  const [inviteUsername, setInviteUsername] = useState("");
  const [invitePermiso, setInvitePermiso] = useState("editar");
  const [inviteMessage, setInviteMessage] = useState("");

  // Ver invitaciones
  const [showInvitationsModal, setShowInvitationsModal] = useState(false);
  const [invitations, setInvitations] = useState([]);
  const [invitationsLoading, setInvitationsLoading] = useState(false);
  const [invitationError, setInvitationError] = useState("");

  // Editar nombre
  const [showEditModal, setShowEditModal] = useState(false);
  const [editingDiagram, setEditingDiagram] = useState(null);
  const [newDiagramName, setNewDiagramName] = useState("");
  const [editMessage, setEditMessage] = useState("");

  // Eliminar
  const [showDeleteModal, setShowDeleteModal] = useState(false);
  const [deletingDiagram, setDeletingDiagram] = useState(null);
  const [deleteMessage, setDeleteMessage] = useState("");

  // Traer usuario
  useEffect(() => {
    const fetchUser = async () => {
      try {
        const token = localStorage.getItem("access_token");
        if (!token) {
          navigate("/");
          return;
        }

        const response = await axiosInstance.get("/user/", {
          headers: { Authorization: `Bearer ${token}` },
        });

        setUser(response.data);
      } catch (err) {
        console.error(err);
        localStorage.removeItem("access_token");
        localStorage.removeItem("refresh_token");
        navigate("/");
      }
    };
    fetchUser();
  }, [navigate]);
  const handleCreateDiagrama = async () => {
    setCreateMessage("");
    
    if (!newDiagramaName.trim()) {
      setCreateMessage("El nombre no puede estar vacío");
      return;
    }

    setCreating(true);
    try {
      const token = localStorage.getItem("access_token");
      const response = await axiosInstance.post(
        "/diagramas/crear_diagrama/",
        { nombre: newDiagramaName.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      // Redirigir al nuevo diagrama
      navigate(`/pizarra/${response.data.id}`);
      
    } catch (err) {
      console.error(err);
      setCreateMessage("Error al crear el diagrama");
    } finally {
      setCreating(false);
    }
  };

  // Traer diagramas
  const fetchData = async () => {
    try {
      const [ultimosData, misData, colabsData] = await Promise.all([
        getUltimosDiagramas(),
        getMisDiagramas(),
        getColaboraciones(),
      ]);
      setUltimos(ultimosData);
      setMisDiagramas(misData);
      setColaboraciones(colabsData);
    } catch (err) {
      console.error("Error cargando diagramas:", err);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  // Manejo dropdown (cerrar si clic fuera)
  useEffect(() => {
    const handleClickOutside = (event) => {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target)) {
        setDropdownOpen(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const handleLogout = () => {
    localStorage.removeItem("access_token");
    localStorage.removeItem("refresh_token");
    navigate("/");
  };

  // Abrir modal de edición
  const handleOpenEdit = (diagrama) => {
    setEditingDiagram(diagrama);
    setNewDiagramName(diagrama.nombre);
    setEditMessage("");
    setShowEditModal(true);
  };

  // Guardar nombre editado
  const handleSaveEdit = async () => {
    setEditMessage("");
    if (!newDiagramName.trim()) {
      setEditMessage("El nombre no puede estar vacío");
      return;
    }
    try {
      const token = localStorage.getItem("access_token");
      await axiosInstance.patch(
        `/diagramas/${editingDiagram.id}/`,
        { nombre: newDiagramName.trim() },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setEditMessage("Nombre actualizado ✅");
      await fetchData(); // Recargar datos
      setTimeout(() => setShowEditModal(false), 800);
    } catch (err) {
      console.error(err);
      setEditMessage("Error al actualizar el nombre");
    }
  };

  // Abrir modal de eliminación
  const handleOpenDelete = (diagrama) => {
    setDeletingDiagram(diagrama);
    setDeleteMessage("");
    setShowDeleteModal(true);
  };

  // Confirmar eliminación
  const handleConfirmDelete = async () => {
    setDeleteMessage("");
    try {
      const token = localStorage.getItem("access_token");
      await axiosInstance.delete(`/diagramas/${deletingDiagram.id}/`, {
        headers: { Authorization: `Bearer ${token}` },
      });
      setDeleteMessage("Diagrama eliminado ✅");
      await fetchData(); // Recargar datos
      setTimeout(() => setShowDeleteModal(false), 800);
    } catch (err) {
      console.error(err);
      setDeleteMessage("Error al eliminar el diagrama");
    }
  };

  // open invite modal (solo para misDiagramas)
  const handleOpenInvite = (diagrama) => {
    setSelectedDiagram(diagrama);
    setInviteUsername("");
    setInvitePermiso("editar");
    setInviteMessage("");
    setShowInviteModal(true);
  };

  // enviar invitación al backend
  const handleSendInvite = async () => {
    setInviteMessage("");
    if (!inviteUsername.trim()) {
      setInviteMessage("Ingresa un username válido");
      return;
    }
    try {
      const token = localStorage.getItem("access_token");
      const payload = {
        diagrama_id: selectedDiagram.id,
        username: inviteUsername.trim(),
        permiso: invitePermiso,
      };
      await axiosInstance.post(
        "/colaboradores/mandar_invitacion/",
        payload,
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setInviteMessage("Invitación enviada ✅");
      setTimeout(() => setShowInviteModal(false), 900);
    } catch (err) {
      console.error(err);
      const msg = err?.response?.data || "Error al enviar invitación";
      setInviteMessage(typeof msg === "string" ? msg : JSON.stringify(msg));
    }
  };

  // abrir modal de invitaciones (traer desde backend)
  const handleOpenInvitations = async () => {
    setInvitationError("");
    setInvitationsLoading(true);
    try {
      const token = localStorage.getItem("access_token");
      const res = await axiosInstance.get(
        "/colaboradores/mostrar_invitacion/",
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setInvitations(res.data || []);
      setShowInvitationsModal(true);
    } catch (err) {
      console.error(err);
      setInvitationError("Error al cargar invitaciones");
    } finally {
      setInvitationsLoading(false);
    }
  };

  // aceptar/rechazar invitacion (PATCH)
  const handleRespondInvitation = async (id, respuesta) => {
    try {
      const token = localStorage.getItem("access_token");
      await axiosInstance.patch(
        "/colaboradores/aceptar_invitacion/",
        { invitacion_id: id, respuesta },
        { headers: { Authorization: `Bearer ${token}` } }
      );
      setInvitations((prev) => prev.filter((i) => i.id !== id));
    } catch (err) {
      console.error(err);
      alert("Error al procesar la invitación");
    }
  };

  // Render
  return (
    <div style={styles.container}>
      {/* Header fijo */}
      <header style={styles.header}>
        <div style={styles.logo} onClick={() => navigate("/dashboard")}>
          <img src="../../public/vite.svg" alt="logo" width="30" />
          <span>Primer Parcial</span>
        </div>

        <div style={styles.searchBox}>
          <input
            type="text"
            placeholder="Buscar diagramas..."
            style={styles.searchInput}
          />
        </div>

        <div
          style={styles.userSection}
          onClick={() => setDropdownOpen(!dropdownOpen)}
          ref={dropdownRef}
        >
          <div style={styles.userCircle}>
            {user ? user.username[0].toUpperCase() : "?"}
          </div>
          <span>{user?.username || "Usuario"}</span>

          {dropdownOpen && (
            <div style={styles.dropdown}>
              <div style={styles.dropdownItem}>
                {user?.first_name || ""} {user?.last_name || ""}
              </div>

              <div
                style={styles.dropdownItem}
                onClick={() => {
                  setDropdownOpen(false);
                  handleOpenInvitations();
                }}
              >
                Mis invitaciones
              </div>

              <div
                style={{ ...styles.dropdownItem, color: "red" }}
                onClick={handleLogout}
              >
                Cerrar sesión
              </div>
            </div>
          )}
        </div>
      </header>

      {/* Contenido */}
      <main style={styles.main}>
        {/* Últimos modificados */}
        <h2>Recientes</h2>
        <div style={styles.cardRow}>
          <div 
            style={{ ...styles.card, ...styles.newCard, cursor: "pointer" }}
            onClick={() => setShowCreateModal(true)}
          >
            <div style={styles.cardPreview}>+</div>
            <div style={styles.cardTitle}>Nuevo diagrama</div>
          </div>
          {ultimos.map((d) => (
            <div
              key={d.id}
              style={{ ...styles.card, cursor: "pointer" }}
              onClick={() => navigate(`/pizarra/${d.id}`)}
            >
              <div style={styles.cardPreview}>📄</div>
              <div style={styles.cardTitle}>
                {d.nombre} <br />
                <small>
                  {new Date(d.fecha_modificacion).toLocaleDateString()}
                </small>
              </div>
            </div>
          ))}
        </div>
        {showCreateModal && (
          <div
            style={styles.modalOverlay}
            onClick={() => setShowCreateModal(false)}
          >
            <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
              <h3>Crear nuevo diagrama</h3>

              <label>Nombre del diagrama</label>
              <input
                type="text"
                value={newDiagramaName}
                onChange={(e) => setNewDiagramaName(e.target.value)}
                onKeyPress={(e) => e.key === "Enter" && handleCreateDiagrama()}
                placeholder="Ej: Sistema de ventas"
                style={{
                  width: "95%",
                  padding: "8px",
                  margin: "8px 0",
                  border: "1px solid #ccc",
                  borderRadius: "6px",
                }}
                autoFocus
              />
  
              <div style={{ marginTop: 12 }}>
                <button 
                  style={styles.button} 
                  onClick={handleCreateDiagrama}
                  disabled={creating}
                >
                  {creating ? "Creando..." : "Crear"}
                </button>
                <button
                  style={{ ...styles.button, background: "gray", marginLeft: 8 }}
                  onClick={() => {
                    setShowCreateModal(false);
                    setNewDiagramaName("");
                    setCreateMessage("");
                  }}
                  disabled={creating}
                >
                  Cancelar
                </button>
              </div>

              {createMessage && (
              <p
                  style={{
                    marginTop: 10,
                    color: createMessage.includes("Error") ? "red" : "green",
                  }}
                >
                  {createMessage}
                </p>
              )}
            </div>
          </div>
        )}

        {/* Mis diagramas */}
        <h2>Mis diagramas</h2>
        <div style={styles.cardRow}>
          {misDiagramas.map((d) => (
            <div key={d.id} style={styles.card}>
              <div
                style={{ ...styles.cardPreview, cursor: "pointer" }}
                onClick={() => navigate(`/pizarra/${d.id}`)}
              >
                📄
              </div>
              <div
                style={{ ...styles.cardTitle, cursor: "pointer" }}
                onClick={() => navigate(`/pizarra/${d.id}`)}
              >
                {d.nombre} <br />
                <small>
                  {new Date(d.fecha_modificacion).toLocaleDateString()}
                </small>
              </div>
              
              <div style={styles.actionButtons}>
                <button
                  style={styles.editButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenEdit(d);
                  }}
                  title="Editar nombre"
                >
                  ✏️
                </button>
                <button
                  style={styles.deleteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenDelete(d);
                  }}
                  title="Eliminar diagrama"
                >
                  🗑️
                </button>
                <button
                  style={styles.inviteButton}
                  onClick={(e) => {
                    e.stopPropagation();
                    handleOpenInvite(d);
                  }}
                >
                  Invitar
                </button>
              </div>
            </div>
          ))}
        </div>

        {/* Colaboraciones */}
        <h2>Colaboraciones</h2>
        <div style={styles.cardRow}>
          {colaboraciones.map((c) => (
            <div
              key={c.id}
              style={{ ...styles.card, cursor: "pointer" }}
              onClick={() => navigate(`/pizarra/${c.id}`)}
            >
              <div style={styles.cardPreview}>👥</div>
              <div style={styles.cardTitle}>
                {c.nombre} <br />
                <small>
                  {new Date(c.fecha_modificacion).toLocaleDateString()}
                </small>
              </div>
            </div>
          ))}
        </div>
      </main>
      {/* ✅ MODAL FUERA del main, al mismo nivel que tus otros modales */}
      {showCreateModal && (
        <div
          style={styles.modalOverlay}
          onClick={() => setShowCreateModal(false)}
        >
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>Crear nuevo diagrama</h3>

            <label>Nombre del diagrama</label>
            <input
              type="text"
              value={newDiagramaName}
              onChange={(e) => setNewDiagramaName(e.target.value)}
              onKeyPress={(e) => e.key === "Enter" && handleCreateDiagrama()}
              placeholder="Ej: Sistema de ventas"
              style={{
                width: "95%",
                padding: "8px",
                margin: "8px 0",
                border: "1px solid #ccc",
                borderRadius: "6px",
              }}
              autoFocus
            />
      
            <div style={{ marginTop: 12 }}>
              <button 
                style={styles.button} 
                onClick={handleCreateDiagrama}
                disabled={creating}
              >
                {creating ? "Creando..." : "Crear"}
              </button>
              <button
                style={{ ...styles.button, background: "gray", marginLeft: 8 }}
                onClick={() => {
                  setShowCreateModal(false);
                  setNewDiagramaName("");
                  setCreateMessage("");
                }}
                disabled={creating}
              >
                Cancelar
              </button>
            </div>

            {createMessage && (
              <p
                style={{
                  marginTop: 10,
                  color: createMessage.includes("Error") ? "red" : "green",
                }}
              >
                {createMessage}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Modal de editar nombre */}
      {showEditModal && (
        <div
          style={styles.modalOverlay}
          onClick={() => setShowEditModal(false)}
        >
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>Editar nombre del diagrama</h3>

            <label>Nuevo nombre</label>
            <input
              type="text"
              value={newDiagramName}
              onChange={(e) => setNewDiagramName(e.target.value)}
              style={{
                width: "95%",
                padding: "8px",
                margin: "8px 0",
                border: "1px solid #ccc",
                borderRadius: "6px",
              }}
            />

            <div style={{ marginTop: 12 }}>
              <button style={styles.button} onClick={handleSaveEdit}>
                Guardar
              </button>
              <button
                style={{ ...styles.button, background: "gray", marginLeft: 8 }}
                onClick={() => setShowEditModal(false)}
              >
                Cancelar
              </button>
            </div>

            {editMessage && (
              <p
                style={{
                  marginTop: 10,
                  color: editMessage.includes("Error") ? "red" : "green",
                }}
              >
                {editMessage}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Modal de confirmar eliminación */}
      {showDeleteModal && (
        <div
          style={styles.modalOverlay}
          onClick={() => setShowDeleteModal(false)}
        >
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>¿Eliminar diagrama?</h3>
            <p>
              ¿Estás seguro de que deseas eliminar "{deletingDiagram?.nombre}"?
              Esta acción no se puede deshacer.
            </p>

            <div style={{ marginTop: 12 }}>
              <button
                style={{ ...styles.button, background: "tomato" }}
                onClick={handleConfirmDelete}
              >
                Eliminar
              </button>
              <button
                style={{ ...styles.button, background: "gray", marginLeft: 8 }}
                onClick={() => setShowDeleteModal(false)}
              >
                Cancelar
              </button>
            </div>

            {deleteMessage && (
              <p
                style={{
                  marginTop: 10,
                  color: deleteMessage.includes("Error") ? "red" : "green",
                }}
              >
                {deleteMessage}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Modal de invitación */}
      {showInviteModal && (
        <div
          style={styles.modalOverlay}
          onClick={() => setShowInviteModal(false)}
        >
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>Invitar a "{selectedDiagram?.nombre}"</h3>

            <label>Usuario</label>
            <input
              type="text"
              placeholder="username"
              value={inviteUsername}
              onChange={(e) => setInviteUsername(e.target.value)}
              style={{
                width: "95%",
                padding: "8px",
                margin: "8px 0",
                border: "1px solid #ccc",
                borderRadius: "6px",
              }}
            />
      
            <label>Permiso</label>
            <select
              value={invitePermiso}
              onChange={(e) => setInvitePermiso(e.target.value)}
              style={{
                width: "95%",
                padding: "8px",
                margin: "8px 0",
                border: "1px solid #ccc",
                borderRadius: "6px",
              }}
            >
              <option value="editar">editar</option>
              <option value="vista">vista</option>
            </select>
      
            <div style={{ marginTop: 8 }}>
              <button style={styles.button} onClick={handleSendInvite}>
                Mandar
              </button>
              <button
                style={{ ...styles.button, background: "gray", marginLeft: 8 }}
                onClick={() => setShowInviteModal(false)}
              >
                Cancelar
              </button>
            </div>
      
            {inviteMessage && (
              <p
                style={{
                  marginTop: 10,
                  color: inviteMessage.includes("Error") ? "red" : "green",
                }}
              >
                {inviteMessage}
              </p>
            )}
          </div>
        </div>
      )}

      {/* Modal de mis invitaciones */}
      {showInvitationsModal && (
        <div
          style={styles.modalOverlay}
          onClick={() => setShowInvitationsModal(false)}
        >
          <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
            <h3>Invitaciones pendientes</h3>
            {invitationsLoading ? (
              <p>Cargando...</p>
            ) : invitationError ? (
              <p style={{ color: "red" }}>{invitationError}</p>
            ) : invitations.length === 0 ? (
              <p>No hay invitaciones pendientes</p>
            ) : (
              <div>
                {invitations.map((inv) => (
                  <div key={inv.id} style={{ marginBottom: 8, borderBottom: "1px solid #eee", paddingBottom: 6 }}>
                    <div>
                      <strong>Diagrama:</strong> {inv.diagrama_nombre ?? "—"}
                    </div>
                    <div style={{ marginTop: 6 }}>
                      <button
                        style={{ ...styles.button, marginRight: 6 }}
                        onClick={() => handleRespondInvitation(inv.id, true)}
                      >
                        Aceptar
                      </button>
                      <button
                        style={{ ...styles.button, background: "tomato" }}
                        onClick={() => handleRespondInvitation(inv.id, false)}
                      >
                        Rechazar
                      </button>
                    </div>
                  </div>
                ))}
              </div>
            )}

            <div style={{ textAlign: "right", marginTop: 10 }}>
              <button style={styles.button} onClick={() => setShowInvitationsModal(false)}>
                Cerrar
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}