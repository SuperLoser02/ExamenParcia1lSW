import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { Stage, Layer, Rect, Text, Line, Arrow, Group } from "react-konva";
import { connectWebSocket, closeWebSocket, sendMessage } from "../services/websocket";
import styles from "../styles/pizarraStyles";


export default function Pizarra() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [tablas, setTablas] = useState([]);
  const [atributos, setAtributos] = useState({});
  const [relaciones, setRelaciones] = useState([]);
  const [diagramaNombre, setDiagramaNombre] = useState(`Diagrama ${id}`);
  
  // Referencias y estados
  const inactivityTimer = useRef(null);
  const socketRef = useRef(null);
  const stageRef = useRef(null);
  
  
  // Estados de UI
  const [sidebarVisible, setSidebarVisible] = useState(true);
  const [herramientaActiva, setHerramientaActiva] = useState(null);
  const [editandoUsuario, setEditandoUsuario] = useState(null);
  const [stagePos, setStagePos] = useState({ x: 0, y: 0 });
  const [isDraggingStage, setIsDraggingStage] = useState(false);
  
  // Estados para IA
  const [isRecording, setIsRecording] = useState(false);
  const [textoComando, setTextoComando] = useState("");
  const [respuestaIA, setRespuestaIA] = useState(null);

  // ========== 1. AGREGAR ESTADOS (después de los estados existentes) ==========
  const [normalizando, setNormalizando] = useState(false);
  const [resultadoNormalizacion, setResultadoNormalizacion] = useState(null);

  const mediaRecorderRef = useRef(null);
  const audioChunksRef = useRef([]);
  // Estados para crear tablas
  const [showCrearTablaModal, setShowCrearTablaModal] = useState(false);
  const [nuevaTablaPos, setNuevaTablaPos] = useState({ x: 0, y: 0 });
  const [nombreTabla, setNombreTabla] = useState("");

  // Agregar estado para loading
  const [generandoArchivo, setGenerandoArchivo] = useState(false);
  
  // Estados para gestionar atributos
  const [showAtributosModal, setShowAtributosModal] = useState(false);
  const [tablaSeleccionada, setTablaSeleccionada] = useState(null);
  const [showAgregarAtributoModal, setShowAgregarAtributoModal] = useState(false);
  const [nuevoAtributo, setNuevoAtributo] = useState({
    nombre: "",
    tipo_dato: "integer",
    primary_key: false,
    is_nullable: false,
    rango: "",
    auto_increment: false,
    solo_positivo: false
  });

  // Agregar estos estados después de los existentes
  const [showEditarTablaModal, setShowEditarTablaModal] = useState(false);
  const [tablaAEditar, setTablaAEditar] = useState(null);
  const [nuevoNombreTabla, setNuevoNombreTabla] = useState("");

  const [showEditarAtributoModal, setShowEditarAtributoModal] = useState(false);
  const [atributoAEditar, setAtributoAEditar] = useState(null);
  
  // Estados para relaciones
  const [relacionEnProgreso, setRelacionEnProgreso] = useState({
    tipo: null,
    tablaOrigen: null,
    tablaDestino: null
  });
  const [showCardinalidadModal, setShowCardinalidadModal] = useState(false);
  const [cardinalidades, setCardinalidades] = useState({
    origen: "1",
    destino: "1"
  });
  const [showTablaResultanteModal, setShowTablaResultanteModal] = useState(false);

  // Resetear contador de inactividad
  const resetInactivityTimer = () => {
    if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
    inactivityTimer.current = setTimeout(() => {
      if (socketRef.current) {
        closeWebSocket();
        socketRef.current = null;
      }
      navigate("/dashboard");
    }, 10 * 60 * 1000);
  };

  // Cerrar sesión
  const handleCerrarSesion = () => {
    if (socketRef.current) {
      closeWebSocket();
      socketRef.current = null;
    }
    navigate("/dashboard");
  };

  // Pedir datos iniciales
  const fetchTablas = () => {
    sendMessage({
      accion: "tabla.getAll",
      payload: { diagrama_id: id },
    });
  };

  const fetchAtributos = (tabla_id) => {
    sendMessage({
      accion: "atributo.getAll",
      payload: { tabla_id },
    });
  };

  const fetchRelaciones = () => {
    sendMessage({
      accion: "relacion.getAll",
      payload: { diagrama_id: id },
    });
  };

  // Conexión WebSocket
  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    if (!socketRef.current) {
      socketRef.current = connectWebSocket(
        id,
        token,
        (data) => {
          const { accion, payload } = data;

          switch (accion) {
            case "tabla.agregar":
              setTablas((prev) => [...prev, payload]);
              break;
            case "tabla.actualizar":
              setTablas((prev) =>
                prev.map((t) => (t.id === payload.id ? payload : t))
              );
              break;
            case "tabla.eliminar":
              fetchTablas();
              break;
            case "tabla.getAll":
              setTablas(payload);
              payload.forEach((t) => fetchAtributos(t.id));
              break;
            case "atributo.agregar":
              setAtributos((prev) => {
                const tablaId = payload.tabla_id;
                const prevAttrs = prev[tablaId] || [];
                return { ...prev, [tablaId]: [...prevAttrs, payload] };
              });
              break;
            case "atributo.actualizar":
              setAtributos((prev) => {
                const tablaId = payload.tabla_id;
                const prevAttrs = prev[tablaId] || [];
                return {
                  ...prev,
                  [tablaId]: prevAttrs.map((a) =>
                    a.id === payload.id ? payload : a
                  ),
                };
              });
              break;
            case "atributo.eliminar":
              // Opción 1: Si tu backend devuelve tabla_id en el payload
              if (payload.tabla_id) {
                setAtributos((prev) => {
                  const prevAttrs = prev[payload.tabla_id] || [];
                  return {
                    ...prev,
                    [payload.tabla_id]: prevAttrs.filter((a) => a.id !== payload.id),
                  };
                });
              } else {
                // Opción 2: Si NO devuelve tabla_id, refrescar todas las tablas
                fetchTablas();
              }
              break;
            case "atributo.getAll":
              setAtributos((prev) => ({
                ...prev,
                [payload.tabla_id]: payload.atributos,
              }));
              break;
            case "relacion.agregar":
              setRelaciones((prev) => [...prev, payload]);
              break;
            case "relacion.actualizar":
              setRelaciones((prev) =>
                prev.map((r) => (r.id === payload.id ? payload : r))
              );
              break;
            case "relacion.eliminar":
              fetchRelaciones();
              break;
            case "relacion.getAll":
              setRelaciones(payload);
              break;
            // Agregar en el switch del WebSocket
            case "generar.sql":
              // Descargar archivo SQL
              const sqlBlob = new Blob([payload.contenido], { type: 'application/sql' });
              const sqlUrl = window.URL.createObjectURL(sqlBlob);
              const sqlLink = document.createElement('a');
              sqlLink.href = sqlUrl;
              sqlLink.download = payload.nombre_archivo;
              sqlLink.click();
              window.URL.revokeObjectURL(sqlUrl);
              setGenerandoArchivo(false);
              break;

            case "generar.springboot":
              // Decodificar base64 y descargar ZIP
              const zipBytes = Uint8Array.from(atob(payload.contenido), c => c.charCodeAt(0));
              const zipBlob = new Blob([zipBytes], { type: 'application/zip' });
              const zipUrl = window.URL.createObjectURL(zipBlob);
              const zipLink = document.createElement('a');
              zipLink.href = zipUrl;
              zipLink.download = payload.nombre_archivo;
              zipLink.click();
              window.URL.revokeObjectURL(zipUrl);
              setGenerandoArchivo(false);
              break;

            case "ia_response":
              setRespuestaIA(payload);
              console.log("Respuesta IA:", payload);
              if (payload.success) {
              // Refrescar tablas y relaciones
              fetchTablas();
              fetchRelaciones();
              }
              break;
            case "diagrama_actualizado":
              if (payload.cambios?.tipo === 'normalizacion') {
                fetchTablas();
                fetchRelaciones();
              }
              break;

            case "normalizacion_response":
              setNormalizando(false);
              setResultadoNormalizacion(payload);
              
              if (payload.success && payload.cambios_realizados > 0) {
                setTimeout(() => {
                  fetchTablas();
                  fetchRelaciones();
                }, 500);
              }
              break;
          }
          resetInactivityTimer();
        },
        () => {
          resetInactivityTimer();
          fetchTablas();
          fetchRelaciones();
        },
        () => {
          socketRef.current = null;
        }
      );
    }

    const activityEvents = ["mousemove", "keydown", "click"];
    activityEvents.forEach((ev) =>
      window.addEventListener(ev, resetInactivityTimer)
    );

    return () => {
      if (inactivityTimer.current) clearTimeout(inactivityTimer.current);
      activityEvents.forEach((ev) =>
        window.removeEventListener(ev, resetInactivityTimer)
      );
    };
  }, [id, navigate]);

  // Manejar click en el stage
  const handleStageClick = (e) => {
    if (herramientaActiva === "tabla") {
      const pos = e.target.getStage().getPointerPosition();
      setNuevaTablaPos(pos);
      setShowCrearTablaModal(true);
      setHerramientaActiva(null);
    } else if (herramientaActiva && herramientaActiva !== "tabla") {
      // Manejar relaciones
      const clickedShape = e.target;
      if (clickedShape.name() === "tabla") {
        const tablaId = clickedShape.getAttr('tablaId');
        const tabla = tablas.find(t => t.id === tablaId);
        
        if (!relacionEnProgreso.tablaOrigen) {
          setRelacionEnProgreso(prev => ({
            ...prev,
            tablaOrigen: tabla
          }));
        } else if (!relacionEnProgreso.tablaDestino) {
          setRelacionEnProgreso(prev => ({
            ...prev,
            tablaDestino: tabla,
            tipo: herramientaActiva
          }));
          
          if (herramientaActiva === "asociacion") {
            setShowCardinalidadModal(true);
          } else {
            crearRelacion(herramientaActiva, relacionEnProgreso.tablaOrigen, tabla);
          }
        }
      }
    }
  };

  // Crear tabla
  const handleCrearTabla = () => {
    if (!nombreTabla.trim()) return;
    
    sendMessage({
      accion: "tabla.agregar",
      payload: {
        nombre: nombreTabla,
        diagrama_id: id,
        pos_x: Math.round(nuevaTablaPos.x),
        pos_y: Math.round(nuevaTablaPos.y),
      },
    });
    
    setNombreTabla("");
    setShowCrearTablaModal(false);
  };

  // Mover tabla
  const handleDragEnd = (e, tabla) => {
    const newPos = {
      pos_x: Math.round(e.target.x()),
      pos_y: Math.round(e.target.y())
    };
    
    sendMessage({
      accion: "tabla.actualizar",
      payload: {
        id: tabla.id,
        ...newPos
      }
    });
  };

  // Doble click en tabla para gestionar atributos
  const handleTablaDoubleClick = (tabla) => {
    setTablaSeleccionada(tabla);
    setShowAtributosModal(true);
  };

  // Función para eliminar tabla
const handleEliminarTabla = (tablaId) => {
  if (window.confirm("¿Estás seguro de eliminar esta tabla? Se eliminarán también sus atributos y relaciones.")) {
    sendMessage({
      accion: "tabla.eliminar",
      payload: { id: tablaId }
    });
    setShowAtributosModal(false);
  }
};

// Función para abrir modal de editar tabla
const handleAbrirEditarTabla = (tabla) => {
  setTablaAEditar(tabla);
  setNuevoNombreTabla(tabla.nombre);
  setShowEditarTablaModal(true);
};

// Función para actualizar nombre de tabla
const handleActualizarTabla = () => {
  if (!nuevoNombreTabla.trim()) return;
  
  sendMessage({
    accion: "tabla.actualizar",
    payload: {
      id: tablaAEditar.id,
      nombre: nuevoNombreTabla,
      diagrama_id: id
    }
  });
  
  setShowEditarTablaModal(false);
  setTablaAEditar(null);
  setNuevoNombreTabla("");
};

  // Crear relación
  const crearRelacion = (tipo, origen, destino, cardOrigen = "1", cardDestino = "1", tablaHijo = null) => {
    sendMessage({
      accion: "relacion.agregar",
      payload: {
        tipo_relacion: tipo,
        tabla_origen: origen.id,
        tabla_destino: destino.id,
        cardinalidad_origen: cardOrigen,
        cardinalidad_destino: cardDestino,
        tabla_hijo: tablaHijo?.id || null,
        diagrama_id: id 
      }
    });
    
    setRelacionEnProgreso({ tipo: null, tablaOrigen: null, tablaDestino: null });
    setHerramientaActiva(null);
  };


  // Modificar la función handleAgregarAtributo
  const handleAgregarAtributo = () => {
    if (!nuevoAtributo.nombre.trim()) return;
  
    sendMessage({
      accion: "atributo.agregar",
      payload: {
        ...nuevoAtributo,
        tabla_id: tablaSeleccionada.id
      }
    });
  
    // Resetear con los valores correctos
    setNuevoAtributo({
      nombre: "",
      tipo_dato: "integer", // ← Cambiar de "INT" a "integer"
      primary_key: false,
      is_nullable: false,
      rango: "",
      auto_increment: false,
      solo_positivo: false
    });
    setShowAgregarAtributoModal(false);
  };

  // Eliminar atributo
  const handleEliminarAtributo = (atributoId) => {
    sendMessage({
      accion: "atributo.eliminar",
      payload: { id: atributoId }
    });
  };

  // Función para abrir modal de editar atributo
  const handleAbrirEditarAtributo = (attr) => {
    setAtributoAEditar(attr);
    setNuevoAtributo({
      nombre: attr.nombre,
      tipo_dato: attr.tipo_dato,
      primary_key: attr.primary_key,
      is_nullable: attr.is_nullable,
      rango: attr.rango || "",
      auto_increment: attr.auto_increment,
      solo_positivo: attr.solo_positivo
    });
    setShowEditarAtributoModal(true);
  };

  // Función para generar SQL
  const handleGenerarSQL = () => {
    setGenerandoArchivo(true);
    sendMessage({
      accion: "generar.sql",
      payload: { diagrama_id: id }
    });
  };

  // Función para generar Spring Boot
  const handleGenerarSpringBoot = () => {
    setGenerandoArchivo(true);
    sendMessage({
      accion: "generar.springboot",
      payload: { diagrama_id: id }
    });
  };

// Función para actualizar atributo
const handleActualizarAtributo = () => {
  if (!nuevoAtributo.nombre.trim()) return;
  
  sendMessage({
    accion: "atributo.actualizar",
    payload: {
      id: atributoAEditar.id,
      ...nuevoAtributo,
      tabla_id: atributoAEditar.tabla_id
    }
  });
  
  setNuevoAtributo({
    nombre: "",
    tipo_dato: "integer",
    primary_key: false,
    is_nullable: false,
    rango: "",
    auto_increment: false,
    solo_positivo: false
  });
  setShowEditarAtributoModal(false);
  setAtributoAEditar(null);
};

  // Calcular dimensiones de tabla
  const calcularDimensionesTabla = (tabla) => {
    const attrs = atributos[tabla.id] || [];
    const minHeight = 60;
    const attrHeight = 25;
    const height = Math.max(minHeight, 40 + (attrs.length * attrHeight));
    return { width: 180, height };
  };

  // Modificar la función renderTabla para mostrar el label correcto
  const renderTabla = (tabla) => {
    const { width, height } = calcularDimensionesTabla(tabla);
    const attrs = atributos[tabla.id] || [];

    return (
      <Group
        key={tabla.id}
        x={tabla.pos_x}
        y={tabla.pos_y}
        draggable={!herramientaActiva}
        onDragEnd={(e) => handleDragEnd(e, tabla)}
        onDblClick={() => handleTablaDoubleClick(tabla)}
      >
        <Rect
          width={width}
          height={height}
          fill="#ffffff"
          stroke="#2563eb"
          strokeWidth={2}
          cornerRadius={8}
          shadowColor="#000000"
          shadowOffset={{ x: 2, y: 2 }}
          shadowOpacity={0.1}
          shadowBlur={4}
          name="tabla"
          tablaId={tabla.id}
        />
        <Text
          x={10}
          y={10}
          text={tabla.nombre}
          fontSize={16}
          fontStyle="bold"
          fill="#1f2937"
          width={width - 20}
        />
        <Line
          points={[10, 35, width - 10, 35]}
          stroke="#e5e7eb"
          strokeWidth={1}
        />
        {attrs.map((attr, index) => (
          <Text
            key={attr.id}
            x={10}
            y={45 + (index * 25)}
            text={`${attr.nombre}: ${getTipoDatoLabel(attr.tipo_dato)}${attr.primary_key ? ' (PK)' : ''}`}
            fontSize={12}
            fill={attr.primary_key ? "#dc2626" : "#4b5563"}
            width={width - 20}
          />
        ))}
      </Group>
    );
  };
  // Función para eliminar relación
  const handleEliminarRelacion = (relacionId) => {
    if (window.confirm("¿Estás seguro de eliminar esta relación?")) {
      sendMessage({
        accion: "relacion.eliminar",
        payload: { id: relacionId }
      });
    }
  };
  // ========== 2. FUNCIÓN PARA NORMALIZAR (después de las funciones existentes) ==========
  const handleNormalizar = () => {
    if (window.confirm("¿Deseas normalizar automáticamente este diagrama?\n\nLa IA analizará las tablas actuales y aplicará formas normales (1FN, 2FN, 3FN).")) {
      setNormalizando(true);
      setResultadoNormalizacion(null);
      
      sendMessage({
        type: "normalizar_diagrama",
        diagrama_id: id
      });
    }
  };
  // Renderizar relación
  const renderRelacion = (relacion) => {
    const origen = tablas.find(t => t.id === relacion.tabla_origen);
    const destino = tablas.find(t => t.id === relacion.tabla_destino);
    
    if (!origen || !destino) return null;
    
    const origenDim = calcularDimensionesTabla(origen);
    const destinoDim = calcularDimensionesTabla(destino);
    
    const startX = origen.pos_x + origenDim.width / 2;
    const startY = origen.pos_y + origenDim.height / 2;
    const endX = destino.pos_x + destinoDim.width / 2;
    const endY = destino.pos_y + destinoDim.height / 2;
    
    const getStrokeColor = (tipo) => {
      switch(tipo) {
        case "herencia": return "#10b981";
        case "asociacion": return "#3b82f6";
        case "composicion": return "#ef4444";
        case "agregacion": return "#f59e0b";
        default: return "#6b7280";
      }
    };
    
    return (
      <Group 
      key={relacion.id}
      onClick={() => {
        if (!herramientaActiva && window.confirm("¿Eliminar esta relación?")) {
          handleEliminarRelacion(relacion.id);
        }
      }} 
      >
        <Line
          points={[startX, startY, endX, endY]}
          stroke={getStrokeColor(relacion.tipo_relacion)}
          strokeWidth={2}
          hitStrokeWidth={20}
        />
        {relacion.tipo_relacion === "herencia" && (
          <Line
            points={[endX - 10, endY - 5, endX, endY, endX - 10, endY + 5]}
            stroke={getStrokeColor(relacion.tipo_relacion)}
            strokeWidth={2}
            fill="transparent"
          />
        )}
      </Group>
    );
  };
  const getTipoDatoLabel = (value) => {
    const tipo = TIPOS_DATO_OPCIONES.find(t => t.value === value);
    return tipo ? tipo.label : value;
  };
  // ========== FUNCIONES DE IA ==========
  const iniciarGrabacion = async () => {
    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      const mediaRecorder = new MediaRecorder(stream);
    
      mediaRecorderRef.current = mediaRecorder;
      audioChunksRef.current = [];

      mediaRecorder.ondataavailable = (event) => {
        audioChunksRef.current.push(event.data);
      };
  
      mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunksRef.current, { type: "audio/webm" });
        enviarAudio(audioBlob);
      };
  
      mediaRecorder.start();
      setIsRecording(true);
    } catch (error) {
      console.error("Error accediendo al micrófono:", error);
      alert("No se pudo acceder al micrófono");
    }
  };

  const detenerGrabacion = () => {
    if (mediaRecorderRef.current && isRecording) {
      mediaRecorderRef.current.stop();
      mediaRecorderRef.current.stream.getTracks().forEach(track => track.stop());
      setIsRecording(false);
    }
  };
  
  const enviarAudio = async (audioBlob) => {
    const reader = new FileReader();
    reader.onloadend = () => {
      const base64Audio = reader.result.split(",")[1];
      
      sendMessage({
        type: "ia_command",
        audio: base64Audio,
        diagrama_id: id
      });
    };
    reader.readAsDataURL(audioBlob);
  };
  
  const enviarTexto = () => {
    if (!textoComando.trim()) {
      alert("Escribe un comando");
      return;
    }
  
    sendMessage({
      type: "ia_command",
      texto: textoComando,
      diagrama_id: id
    });

    setTextoComando("");
  };

  const TIPOS_DATO_OPCIONES = [
    { value: "integer", label: "INT" },
    { value: "smallint", label: "SMALLINT" },
    { value: "bigint", label: "BIGINT" },
    { value: "float", label: "FLOAT" },
    { value: "decimal", label: "DECIMAL" },
    { value: "char", label: "VARCHAR" },
    { value: "text", label: "TEXT" },
    { value: "boolean", label: "TINYINT" },
    { value: "date", label: "DATE" },
    { value: "datetime", label: "DATETIME" },
    { value: "time", label: "TIME" },
    { value: "json", label: "JSON" }
  ];

  return( 
  <div style={styles.container}>
    {/* ========== HEADER ========== */}
    <header style={styles.header}>
      <h1 style={styles.headerTitle}>{diagramaNombre}</h1>
  
      <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
        <button
          onClick={handleGenerarSQL}
          disabled={generandoArchivo}
          style={{
            backgroundColor: "#10b981",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: generandoArchivo ? "not-allowed" : "pointer",
            fontWeight: "500",
            opacity: generandoArchivo ? 0.6 : 1
          }}
        >
          {generandoArchivo ? "Generando..." : "Generar SQL"}
        </button>
        <button
          onClick={handleNormalizar}
          disabled={normalizando || generandoArchivo}
          style={{
            backgroundColor: "#8b5cf6",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: normalizando ? "not-allowed" : "pointer",
            fontWeight: "500",
            opacity: normalizando ? 0.6 : 1
          }}
        >
          {normalizando ? "Normalizando..." : "🔧 Normalizar"}
        </button>
        
        <button
          onClick={handleGenerarSpringBoot}
          disabled={generandoArchivo}
          style={{
            backgroundColor: "#3b82f6",
            color: "white",
            border: "none",
            padding: "8px 16px",
            borderRadius: "6px",
            cursor: generandoArchivo ? "not-allowed" : "pointer",
            fontWeight: "500",
            opacity: generandoArchivo ? 0.6 : 1
          }}
        >
          {generandoArchivo ? "Generando..." : "Generar Spring Boot"}
        </button>
        
        <button onClick={handleCerrarSesion} style={styles.btnCerrarSesion}>
          Cerrar sesión
        </button>
      </div>
    </header>

    {/* ========== LAYOUT PRINCIPAL ========== */}
    <div style={styles.mainLayout}>
      
      {/* ========== SIDEBAR (COLUMNA) ========== */}
      {sidebarVisible && (
        <div style={styles.sidebar}>
          <h3 style={styles.sidebarTitle}>Herramientas UML</h3>
          
          <div style={styles.herramientasContainer}>
            {/* Botón Clase/Tabla */}
            <button
              onClick={() => setHerramientaActiva(herramientaActiva === "tabla" ? null : "tabla")}
              style={{
                ...styles.btnHerramienta,
                ...(herramientaActiva === "tabla" ? styles.btnHerramientaActiva : {})
              }}
            >
              <div style={styles.iconoTabla}></div>
              Clase/Tabla
            </button>

            {/* Botón Herencia */}
            <button
              onClick={() => setHerramientaActiva(herramientaActiva === "herencia" ? null : "herencia")}
              style={{
                ...styles.btnHerramienta,
                ...(herramientaActiva === "herencia" ? { ...styles.btnHerramientaActiva, backgroundColor: "#f0fdf4", borderColor: "#10b981" } : {})
              }}
            >
              <div style={styles.iconoHerencia}>
                <div style={styles.flechaHerencia}></div>
              </div>
              Herencia
            </button>

            {/* Botón Asociación */}
            <button
              onClick={() => setHerramientaActiva(herramientaActiva === "asociacion" ? null : "asociacion")}
              style={{
                ...styles.btnHerramienta,
                ...(herramientaActiva === "asociacion" ? styles.btnHerramientaActiva : {})
              }}
            >
              <div style={styles.iconoAsociacion}></div>
              Asociación
            </button>

            {/* Botón Composición */}
            <button
              onClick={() => setHerramientaActiva(herramientaActiva === "composicion" ? null : "composicion")}
              style={{
                ...styles.btnHerramienta,
                ...(herramientaActiva === "composicion" ? { ...styles.btnHerramientaActiva, backgroundColor: "#fef2f2", borderColor: "#ef4444" } : {})
              }}
            >
              <div style={styles.iconoComposicion}></div>
              Composición
            </button>

            {/* Botón Agregación */}
            <button
              onClick={() => setHerramientaActiva(herramientaActiva === "agregacion" ? null : "agregacion")}
              style={{
                ...styles.btnHerramienta,
                ...(herramientaActiva === "agregacion" ? { ...styles.btnHerramientaActiva, backgroundColor: "#fffbeb", borderColor: "#f59e0b" } : {})
              }}
            >
              <div style={styles.iconoAgregacion}></div>
              Agregación
            </button>
          </div>

          {/* Información de herramienta activa */}
          {herramientaActiva && (
            <div style={styles.infoHerramienta}>
              {herramientaActiva === "tabla" && "Haz clic en la pizarra para crear una tabla"}
              {herramientaActiva === "herencia" && "Selecciona tabla padre, luego tabla hija"}
              {herramientaActiva === "asociacion" && "Selecciona tabla origen, luego tabla destino"}
              {herramientaActiva === "composicion" && "Selecciona tabla todo, luego tabla parte"}
              {herramientaActiva === "agregacion" && "Selecciona tabla todo, luego tabla parte"}
            </div>
          )}

          {/* Información de relación en progreso */}
          {relacionEnProgreso.tablaOrigen && (
            <div style={styles.infoRelacionProgreso}>
              <strong>Origen:</strong> {relacionEnProgreso.tablaOrigen.nombre}
              <br />
              {relacionEnProgreso.tablaDestino ? 
                <><strong>Destino:</strong> {relacionEnProgreso.tablaDestino.nombre}</> : 
                "Selecciona tabla destino..."
              }
            </div>
          )}
        </div>
      )}

      {/* ========== BOTÓN TOGGLE SIDEBAR ========== */}
      <button
        onClick={() => setSidebarVisible(!sidebarVisible)}
        style={{
          ...styles.btnToggleSidebar,
          ...(sidebarVisible ? {} : styles.btnToggleSidebarClosed)
        }}
      >
        <div style={styles.iconoMenuBurger}>
          <div style={styles.lineaMenuBurger}></div>
          <div style={styles.lineaMenuBurger}></div>
          <div style={styles.lineaMenuBurger}></div>
        </div>
      </button>

      {/* ========== PIZARRA (STAGE KONVA) ========== */}
      <div style={styles.pizarraContainer}>
        <Stage
          width={window.innerWidth - (sidebarVisible ? 240 : 0)}
          height={window.innerHeight - 60}
          onClick={handleStageClick}
          onContextMenu={(e) => e.evt.preventDefault()}
          draggable
          ref={stageRef}
        >
          <Layer>
            {/* Renderizar relaciones */}
            {relaciones.map(renderRelacion)}
            
            {/* Renderizar tablas */}
            {tablas.map(renderTabla)}
          </Layer>
        </Stage>
      </div>
    </div>

    {/* ========== MODAL: CREAR TABLA ========== */}
    {showCrearTablaModal && (
      <div style={styles.modalOverlay} onClick={() => setShowCrearTablaModal(false)}>
        <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
          <h3 style={styles.modalTitle}>Nueva tabla...</h3>
          
          <input
            type="text"
            placeholder="Nombre de la tabla"
            value={nombreTabla}
            onChange={(e) => setNombreTabla(e.target.value)}
            style={styles.input}
            autoFocus
            onKeyPress={(e) => e.key === "Enter" && handleCrearTabla()}
          />
          
          <div style={styles.btnGroup}>
            <button onClick={() => setShowCrearTablaModal(false)} style={styles.btnSecondary}>
              Cancelar
            </button>
            <button
              onClick={handleCrearTabla}
              disabled={!nombreTabla.trim()}
              style={{
                ...styles.btnPrimary,
                ...(!nombreTabla.trim() ? styles.btnDisabled : {})
              }}
            >
              Agregar
            </button>
          </div>
        </div>
      </div>
    )}

    {/* ========== MODAL: GESTIONAR ATRIBUTOS (MODIFICADO) ========== */}
    {showAtributosModal && tablaSeleccionada && (
      <div style={styles.modalOverlay} onClick={() => setShowAtributosModal(false)}>
        <div style={{ ...styles.modal, ...styles.modalLarge }} onClick={(e) => e.stopPropagation()}>
          <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center", marginBottom: "20px" }}>
            <h3 style={{ ...styles.modalTitle, margin: 0 }}>
              Atributos de "{tablaSeleccionada.nombre}"
            </h3>
            <div style={{ display: "flex", gap: "8px" }}>
              <button
                onClick={() => {
                  handleAbrirEditarTabla(tablaSeleccionada);
                  setShowAtributosModal(false);
                }}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#3b82f6",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "12px"
                }}
              >
                Editar Tabla
              </button>
              <button
                onClick={() => handleEliminarTabla(tablaSeleccionada.id)}
                style={{
                  padding: "6px 12px",
                  backgroundColor: "#ef4444",
                  color: "white",
                  border: "none",
                  borderRadius: "4px",
                  cursor: "pointer",
                  fontSize: "12px"
                }}
              >
                Eliminar Tabla
                  </button>
            </div>
          </div>
          
          {/* Lista de atributos */}
          <div style={{ marginBottom: "20px" }}>
            {(atributos[tablaSeleccionada.id] || []).length === 0 ? (
              <div style={styles.emptyState}>No hay atributos</div>
            ) : (
              (atributos[tablaSeleccionada.id] || []).map((attr) => (
                <div key={attr.id} style={styles.atributoItem}>
                  <div style={styles.atributoInfo}>
                    <div style={styles.atributoNombre}>
                      {attr.nombre}
                      {attr.primary_key && <span style={styles.badgePK}>PK</span>}
                      {attr.is_nullable && <span style={styles.badgeNull}>NULL</span>}
                    </div>
                    <div style={styles.atributoDetalle}>
                      {getTipoDatoLabel(attr.tipo_dato)}
                      {attr.rango && ` (${attr.rango})`}
                      {attr.auto_increment && " • AUTO_INCREMENT"}
                      {attr.solo_positivo && " • UNSIGNED"}
                    </div>
                  </div>
                  <div style={{ display: "flex", gap: "6px" }}>
                    <button
                      onClick={() => {
                        handleAbrirEditarAtributo(attr);
                        setShowAtributosModal(false);
                      }}
                      style={{
                        padding: "4px 8px",
                        backgroundColor: "#3b82f6",
                        color: "white",
                        border: "none",
                        borderRadius: "4px",
                        cursor: "pointer",
                        fontSize: "12px"
                      }}
                    >
                      Editar
                    </button>
                    <button
                      onClick={() => handleEliminarAtributo(attr.id)}
                      style={styles.btnDanger}
                    >
                      Eliminar
                    </button>
                  </div>
                </div>
              ))
            )}
          </div>
          
          <div style={styles.btnGroupSpaceBetween}>
            <button onClick={() => setShowAgregarAtributoModal(true)} style={styles.btnSuccess}>
              Agregar Atributo
            </button>
            <button onClick={() => setShowAtributosModal(false)} style={styles.btnSecondary}>
              Cerrar
            </button>
          </div>
        </div>
      </div>
    )}
    
    {/* ========== MODAL: EDITAR TABLA ========== */}
    {showEditarTablaModal && tablaAEditar && (
      <div style={styles.modalOverlay} onClick={() => setShowEditarTablaModal(false)}>
        <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
          <h3 style={styles.modalTitle}>Editar Tabla</h3>
          
          <div style={styles.formGroup}>
            <label style={styles.label}>Nombre de la tabla</label>
            <input
              type="text"
              placeholder="Nombre de la tabla"
              value={nuevoNombreTabla}
              onChange={(e) => setNuevoNombreTabla(e.target.value)}
              style={styles.input}
              autoFocus
              onKeyPress={(e) => e.key === "Enter" && handleActualizarTabla()}
            />
          </div>
          
          <div style={styles.btnGroup}>
            <button onClick={() => setShowEditarTablaModal(false)} style={styles.btnSecondary}>
              Cancelar
            </button>
            <button
              onClick={handleActualizarTabla}
              disabled={!nuevoNombreTabla.trim()}
              style={{
                ...styles.btnPrimary,
                ...(!nuevoNombreTabla.trim() ? styles.btnDisabled : {})
              }}
            >
              Actualizar
            </button>
          </div>
        </div>
      </div>
    )}
    
    {/* ========== MODAL: EDITAR ATRIBUTO ========== */}
    {showEditarAtributoModal && atributoAEditar && (
      <div style={styles.modalOverlay} onClick={() => setShowEditarAtributoModal(false)}>
        <div style={{ ...styles.modal, ...styles.modalLarge }} onClick={(e) => e.stopPropagation()}>
          <h3 style={styles.modalTitle}>Editar Atributo</h3>
          
          <div style={styles.formGroup}>
            <label style={styles.label}>Nombre</label>
            <input
              type="text"
              placeholder="Nombre del atributo"
              value={nuevoAtributo.nombre}
              onChange={(e) => setNuevoAtributo({...nuevoAtributo, nombre: e.target.value})}
              style={styles.input}
            />
          </div>
    
          <div style={styles.formGroup}>
            <label style={styles.label}>Tipo de dato</label>
            <select
              value={nuevoAtributo.tipo_dato}
              onChange={(e) => setNuevoAtributo({...nuevoAtributo, tipo_dato: e.target.value})}
              style={styles.select}
            >
              {TIPOS_DATO_OPCIONES.map(tipo => (
                <option key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </option>
              ))}
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>Rango (opcional)</label>
            <input
              type="text"
              placeholder="Ej: 10,2 para DECIMAL o 255 para VARCHAR"
              value={nuevoAtributo.rango}
              onChange={(e) => setNuevoAtributo({...nuevoAtributo, rango: e.target.value})}
              style={styles.input}
            />
          </div>
    
          <div style={styles.formRow}>
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.primary_key}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, primary_key: e.target.checked})}
                style={styles.checkbox}
              />
              <label style={styles.label}>Es Primary Key</label>
            </div>
    
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.is_nullable}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, is_nullable: e.target.checked})}
                style={styles.checkbox}
              />
              <label style={styles.label}>Puede ser NULL</label>
            </div>
          </div>
    
          <div style={styles.formRow}>
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.auto_increment}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, auto_increment: e.target.checked})}
                style={styles.checkbox}
                disabled={!["integer", "smallint", "bigint"].includes(nuevoAtributo.tipo_dato)}
              />
              <label style={styles.label}>Auto Increment</label>
            </div>
    
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.solo_positivo}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, solo_positivo: e.target.checked})}
                style={styles.checkbox}
                disabled={!["integer", "smallint", "bigint", "float", "decimal"].includes(nuevoAtributo.tipo_dato)}
              />
              <label style={styles.label}>Solo positivos</label>
            </div>
          </div>

          <div style={styles.btnGroup}>
            <button onClick={() => setShowEditarAtributoModal(false)} style={styles.btnSecondary}>
              Cancelar
            </button>
            <button
              onClick={handleActualizarAtributo}
              disabled={!nuevoAtributo.nombre.trim()}
              style={{
                ...styles.btnSuccess,
                ...(!nuevoAtributo.nombre.trim() ? styles.btnDisabled : {})
              }}
            >
              Actualizar
            </button>
          </div>
        </div>
      </div>
    )}

    {/* ========== MODAL: AGREGAR ATRIBUTO ========== */}
    {showAgregarAtributoModal && (
      <div style={styles.modalOverlay} onClick={() => setShowAgregarAtributoModal(false)}>
        <div style={{ ...styles.modal, ...styles.modalLarge }} onClick={(e) => e.stopPropagation()}>
          <h3 style={styles.modalTitle}>Agregar Atributo</h3>
      
          <div style={styles.formGroup}>
            <label style={styles.label}>Nombre</label>
            <input
              type="text"
              placeholder="Nombre del atributo"
              value={nuevoAtributo.nombre}
              onChange={(e) => setNuevoAtributo({...nuevoAtributo, nombre: e.target.value})}
              style={styles.input}
            />
          </div>
    
          <div style={styles.formGroup}>
            <label style={styles.label}>Tipo de dato</label>
            <select
              value={nuevoAtributo.tipo_dato}
              onChange={(e) => setNuevoAtributo({...nuevoAtributo, tipo_dato: e.target.value})}
              style={styles.select}
            >
              {TIPOS_DATO_OPCIONES.map(tipo => (
                <option key={tipo.value} value={tipo.value}>
                  {tipo.label}
                </option>
              ))}
            </select>
          </div>
    
          <div style={styles.formGroup}>
            <label style={styles.label}>Rango (opcional)</label>
            <input
              type="text"
              placeholder="Ej: 10,2 para DECIMAL o 255 para VARCHAR"
              value={nuevoAtributo.rango}
              onChange={(e) => setNuevoAtributo({...nuevoAtributo, rango: e.target.value})}
              style={styles.input}
            />
          </div>
    
          <div style={styles.formRow}>
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.primary_key}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, primary_key: e.target.checked})}
                style={styles.checkbox}
              />
              <label style={styles.label}>Es Primary Key</label>
            </div>
    
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.is_nullable}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, is_nullable: e.target.checked})}
                style={styles.checkbox}
              />
              <label style={styles.label}>Puede ser NULL</label>
            </div>
          </div>
    
          <div style={styles.formRow}>
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.auto_increment}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, auto_increment: e.target.checked})}
                style={styles.checkbox}
                disabled={!["integer", "smallint", "bigint"].includes(nuevoAtributo.tipo_dato)}
              />
              <label style={styles.label}>Auto Increment</label>
            </div>
    
            <div style={styles.checkboxContainer}>
              <input
                type="checkbox"
                checked={nuevoAtributo.solo_positivo}
                onChange={(e) => setNuevoAtributo({...nuevoAtributo, solo_positivo: e.target.checked})}
                style={styles.checkbox}
                disabled={!["integer", "smallint", "bigint", "float", "decimal"].includes(nuevoAtributo.tipo_dato)}
              />
              <label style={styles.label}>Solo positivos</label>
            </div>
          </div>
    
          <div style={styles.btnGroup}>
            <button onClick={() => setShowAgregarAtributoModal(false)} style={styles.btnSecondary}>
              Cancelar
            </button>
            <button
              onClick={handleAgregarAtributo}
              disabled={!nuevoAtributo.nombre.trim()}
              style={{
                ...styles.btnSuccess,
                ...(!nuevoAtributo.nombre.trim() ? styles.btnDisabled : {})
              }}
            >
              Agregar
            </button>
          </div>
        </div>
      </div>
    )}

    {/* ========== MODAL: CARDINALIDAD (ASOCIACIÓN) ========== */}
    {showCardinalidadModal && (
      <div style={styles.modalOverlay}>
        <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
          <h3 style={styles.modalTitle}>Cardinalidad de Asociación</h3>
          
          <div style={styles.formGroup}>
            <label style={styles.label}>
              Cardinalidad Origen ({relacionEnProgreso.tablaOrigen?.nombre})
            </label>
            <select
              value={cardinalidades.origen}
              onChange={(e) => setCardinalidades({...cardinalidades, origen: e.target.value})}
              style={styles.select}
            >
              <option value="0..1">0..1</option>
              <option value="1..1">1..1</option>
              <option value="0..*">0..*</option>
              <option value="1..*">1..*</option>
            </select>
          </div>

          <div style={styles.formGroup}>
            <label style={styles.label}>
              Cardinalidad Destino ({relacionEnProgreso.tablaDestino?.nombre})
            </label>
            <select
              value={cardinalidades.destino}
              onChange={(e) => setCardinalidades({...cardinalidades, destino: e.target.value})}
              style={styles.select}
            >
              <option value="0..1">0..1</option>
              <option value="1..1">1..1</option>
              <option value="0..*">0..*</option>
              <option value="1..*">1..*</option>
            </select>
          </div>

          <div style={styles.btnGroup}>
            <button
              onClick={() => {
                setShowCardinalidadModal(false);
                setRelacionEnProgreso({ tipo: null, tablaOrigen: null, tablaDestino: null });
                setHerramientaActiva(null);
              }}
              style={styles.btnSecondary}
            >
              Cancelar
            </button>
            <button
              onClick={() => {
                if ((cardinalidades.origen.includes("*") && cardinalidades.destino.includes("*"))) {
                  setShowCardinalidadModal(false);
                  setShowTablaResultanteModal(true);
                } else {
                  crearRelacion(
                    "asociacion",
                    relacionEnProgreso.tablaOrigen,
                    relacionEnProgreso.tablaDestino,
                    cardinalidades.origen,
                    cardinalidades.destino
                  );
                  setShowCardinalidadModal(false);
                }
              }}
              style={styles.btnPrimary}
            >
              Continuar
            </button>
          </div>
        </div>
      </div>
    )}

    {/* ========== MODAL: TABLA RESULTANTE (*..*) ========== */}
    {showTablaResultanteModal && (
      <div style={styles.modalOverlay}>
        <div style={styles.modal} onClick={(e) => e.stopPropagation()}>
          <h3 style={styles.modalTitle}>Tabla Resultante (*...*)</h3>
          
          <p style={{ marginBottom: "16px", color: "#6b7280", fontSize: "14px" }}>
            Selecciona una tabla existente que será la tabla resultante de esta relación:
          </p>

          <div style={styles.formGroup}>
            <label style={styles.label}>Tabla Resultante</label>
            <select
              value={relacionEnProgreso.tablaHijo?.id || ""}
              onChange={(e) => {
                const tabla = tablas.find(t => t.id === parseInt(e.target.value));
                setRelacionEnProgreso({...relacionEnProgreso, tablaHijo: tabla});
              }}
              style={styles.select}
            >
              <option value="">Seleccionar tabla...</option>
              {tablas
                .filter(t => 
                  t.id !== relacionEnProgreso.tablaOrigen?.id && 
                  t.id !== relacionEnProgreso.tablaDestino?.id
                )
                .map(t => (
                  <option key={t.id} value={t.id}>{t.nombre}</option>
                ))
              }
            </select>
          </div>

          <div style={styles.btnGroup}>
            <button
              onClick={() => {
                setShowTablaResultanteModal(false);
                setShowCardinalidadModal(false);
                setRelacionEnProgreso({ tipo: null, tablaOrigen: null, tablaDestino: null });
                setHerramientaActiva(null);
              }}
              style={styles.btnSecondary}
            >
              Cancelar
            </button>
            <button
              onClick={() => {
                crearRelacion(
                  "asociacion",
                  relacionEnProgreso.tablaOrigen,
                  relacionEnProgreso.tablaDestino,
                  cardinalidades.origen,
                  cardinalidades.destino,
                  relacionEnProgreso.tablaHijo
                );
                setShowTablaResultanteModal(false);
                setShowCardinalidadModal(false);
              }}
              disabled={!relacionEnProgreso.tablaHijo}
              style={{
                ...styles.btnPrimary,
                ...(!relacionEnProgreso.tablaHijo ? styles.btnDisabled : {})
              }}
            >            
              Crear Relación
            </button>
          </div>
        </div>
      </div>
    )}

    {/* ========== PANEL ASISTENTE IA ========== */}
    <div style={{
      position: "fixed",
      bottom: "20px",
      right: "20px",
      backgroundColor: "#fff",
      padding: "20px",
      borderRadius: "12px",
      boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
      width: "350px",
      zIndex: 1000
    }}>
      <h3 style={{ marginTop: 0 }}>🤖 Asistente IA</h3>
    
      {/* Input de texto */}
      <div style={{ marginBottom: "15px" }}>
        <input
          type="text"
          value={textoComando}
          onChange={(e) => setTextoComando(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && enviarTexto()}
          placeholder="Ej: crea tabla usuarios con id, nombre, email"
          style={{
            width: "100%",
            padding: "10px",
            border: "1px solid #ccc",
            borderRadius: "6px",
            marginBottom: "8px"
          }}
        />
        <button
          onClick={enviarTexto}
          style={{
            width: "100%",
            padding: "10px",
            backgroundColor: "#007bff",
            color: "#fff",
            border: "none",
            borderRadius: "6px",
            cursor: "pointer"
          }}
        >
          Enviar Texto
        </button>
      </div>
    
      {/* Botón de grabación */}
      <button
        onClick={isRecording ? detenerGrabacion : iniciarGrabacion}
        style={{
          width: "100%",
          padding: "15px",
          backgroundColor: isRecording ? "#dc3545" : "#28a745",
          color: "#fff",
          border: "none",
          borderRadius: "6px",
          cursor: "pointer",
          fontSize: "16px",
          fontWeight: "bold"
        }}
      >
        {isRecording ? "🔴 Detener Grabación" : "🎤 Grabar Comando"}
      </button>
    
      {/* Respuesta de la IA */}
      {respuestaIA && (
        <div style={{
          marginTop: "15px",
          padding: "12px",
          backgroundColor: respuestaIA.success ? "#d4edda" : "#f8d7da",
          borderRadius: "6px",
          fontSize: "14px"
        }}>
          <strong>{respuestaIA.success ? "✅ Éxito:" : "❌ Error:"}</strong>
          <p style={{ margin: "5px 0 0 0" }}>{respuestaIA.mensaje}</p>
          
          {respuestaIA.detalles && (
            <ul style={{ marginTop: "8px", paddingLeft: "20px" }}>
              {respuestaIA.detalles.map((detalle, idx) => (
                <li key={idx}>{detalle}</li>
              ))}
            </ul>
          )}
        </div>
      )}
      {resultadoNormalizacion && (
      <div style={styles.modalOverlay} onClick={() => setResultadoNormalizacion(null)}>
        <div 
          style={{ 
            ...styles.modal, 
            ...styles.modalLarge,
            maxWidth: "600px"
          }} 
          onClick={(e) => e.stopPropagation()}
        >
          <h3 style={{
            ...styles.modalTitle,
            color: resultadoNormalizacion.success ? "#059669" : "#dc2626"
          }}>
            {resultadoNormalizacion.success ? "✅ Normalización Completada" : "❌ Error"}
          </h3>
          
          <div style={{ marginBottom: "20px" }}>
            {/* Análisis */}
            {resultadoNormalizacion.analisis && (
              <div style={{
                padding: "12px",
                backgroundColor: "#f3f4f6",
                borderRadius: "6px",
                marginBottom: "15px",
                fontSize: "14px"
              }}>
                <strong>Análisis:</strong>
                <p style={{ margin: "8px 0 0 0" }}>{resultadoNormalizacion.analisis}</p>
              </div>
            )}
            
            {/* Violaciones */}
            {resultadoNormalizacion.violaciones?.length > 0 && (
              <div style={{ marginBottom: "15px" }}>
                <strong style={{ color: "#dc2626", fontSize: "14px" }}>
                  ⚠️ Problemas detectados:
                    </strong>
                <ul style={{ 
                  marginTop: "8px", 
                  paddingLeft: "20px", 
                  fontSize: "13px",
                  color: "#6b7280"
                }}>
                  {resultadoNormalizacion.violaciones.map((v, idx) => (
                    <li key={idx}>{v}</li>
                  ))}
                </ul>
              </div>
            )}
            
            {/* Resultado */}
            <div style={{ 
              padding: "12px", 
              backgroundColor: resultadoNormalizacion.cambios_realizados > 0 ? "#d1fae5" : "#fef3c7",
              borderRadius: "6px",
              marginBottom: "15px"
            }}>
              <strong style={{ fontSize: "14px" }}>
                {resultadoNormalizacion.cambios_realizados > 0 
                  ? `✓ Se realizaron ${resultadoNormalizacion.cambios_realizados} cambios` 
                  : "ℹ️ El diagrama ya está normalizado"}
              </strong>
            </div>
            
            {/* Detalles */}
            {resultadoNormalizacion.detalles?.length > 0 && (
              <div>
                <strong style={{ fontSize: "14px" }}>Detalles:</strong>
                <div style={{ 
                  maxHeight: "250px", 
                  overflowY: "auto", 
                  marginTop: "10px",
                  border: "1px solid #e5e7eb",
                  borderRadius: "6px"
                }}>
                  {resultadoNormalizacion.detalles.map((detalle, idx) => (
                    <div 
                      key={idx}
                      style={{
                        padding: "10px",
                        backgroundColor: detalle.success ? "#f0fdf4" : "#fef2f2",
                        borderBottom: "1px solid #e5e7eb",
                        fontSize: "13px"
                      }}
                    >
                      {detalle.success ? "✓" : "✗"} {detalle.mensaje}
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
          
          <div style={styles.btnGroup}>
            <button 
              onClick={() => setResultadoNormalizacion(null)} 
              style={styles.btnPrimary}
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
    )}
    </div>
  </div>
  );
}