// src/services/diagramaService.js
import axiosInstance from "./axiosInstance";

// últimos 5 modificados
export const getUltimosDiagramas = async () => {
  const response = await axiosInstance.get("/diagramas/ultimos_5_diagramas_modificados/");
  return response.data;
};

// mis diagramas (donde soy dueño)
export const getMisDiagramas = async () => {
  const response = await axiosInstance.get("/diagramas/get_mis_diagramas/");
  return response.data;
};

// colaboraciones
export const getColaboraciones = async () => {
  const response = await axiosInstance.get("/diagramas/diagramas_donde_soy_colaborador/");
  return response.data;
};
