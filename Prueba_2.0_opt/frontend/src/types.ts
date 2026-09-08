/**
 * Contratos de datos e interfaces estrictas en TypeScript para el Frontend.
 * Sincronizados 1:1 con los modelos Pydantic v2 del Backend.
 */

export type MessageRole = 'user' | 'assistant' | 'system';

export interface ChatMessage {
  role: MessageRole;
  content: string;
}

export interface ChatRequest {
  pregunta: string;
  historial?: ChatMessage[];
}

export interface Citation {
  documento: string;
  contenido: string;
  score: number;
}

export type ResponseOrigin = 
  | 'cache' 
  | 'chitchat_greeting'
  | 'rag_ollama_local'
  | 'rag_gemini_flash'
  | 'rag_qdrant' 
  | 'out_of_scope_llm' 
  | 'fallback';

export interface ChatResponse {
  respuesta: string;
  fuentes: Citation[];
  confianza: number;
  escalar_humano: boolean;
  origen: ResponseOrigin;
  tiempo_ms: number;
}

export interface MetricsResponse {
  consultas_totales: number;
  consultas_cache: number;
  consultas_rag: number;
  consultas_escaladas: number;
  tasa_cache_hit_pct: number;
  tasa_escalamiento_pct: number;
  latencia_promedio_ms: number;
  costo_estimado_usd: number;
  tiempo_actividad_segundos: number;
}

export interface IngestResponse {
  status: string;
  documentos_procesados: number;
  total_chunks: number;
  tiempo_ms: number;
}
