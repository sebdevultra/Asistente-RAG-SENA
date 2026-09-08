/**
 * Cliente HTTP fuertemente tipado para la API del Asistente Virtual RAG.
 */

import { ChatRequest, ChatResponse, MetricsResponse, IngestResponse } from './types';

const API_BASE = ''; // Utiliza rutas relativas al mismo host

export async function sendChatMessage(request: ChatRequest): Promise<ChatResponse> {
  const response = await fetch(`${API_BASE}/api/chat`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: 'Error de red desconocido' }));
    throw new Error(errData.detail || `Error HTTP ${response.status}`);
  }

  return response.json();
}

export async function fetchMetrics(): Promise<MetricsResponse> {
  const response = await fetch(`${API_BASE}/api/metrics`);
  if (!response.ok) {
    throw new Error(`Error obteniendo métricas: ${response.statusText}`);
  }
  return response.json();
}

export async function triggerIngestion(adminKey: string): Promise<IngestResponse> {
  const response = await fetch(`${API_BASE}/api/ingest`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
      'X-Admin-Key': adminKey,
    },
  });

  if (!response.ok) {
    const errData = await response.json().catch(() => ({ detail: 'Error en ingestión' }));
    throw new Error(errData.detail || `Error de autorización (${response.status})`);
  }

  return response.json();
}

export async function checkSystemHealth(): Promise<Record<string, unknown>> {
  const response = await fetch(`${API_BASE}/api/health`);
  return response.json();
}
