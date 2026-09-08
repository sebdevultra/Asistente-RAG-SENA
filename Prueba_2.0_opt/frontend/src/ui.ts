/**
 * Componentes y funciones de renderizado del DOM para el Frontend TypeScript.
 */

import { ChatResponse, MetricsResponse, Citation } from './types';

export function createMessageElement(
  sender: 'user' | 'assistant',
  text: string,
  meta?: {
    tiempo_ms?: number;
    origen?: string;
    confianza?: number;
    escalar_humano?: boolean;
    fuentes?: Citation[];
  }
): HTMLElement {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}-message`;

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.innerText = text;
  msgDiv.appendChild(contentDiv);

  if (meta && sender === 'assistant') {
    const metaBar = document.createElement('div');
    metaBar.className = 'message-meta';

    // Badge de origen
    const originBadge = document.createElement('span');
    originBadge.className = `badge origin-${meta.origen || 'unknown'}`;
    const originNames: Record<string, string> = {
      cache: '⚡ SQLite WAL Cache (<2ms)',
      chitchat_greeting: '💬 Saludo / Cortesía',
      rag_ollama_local: '🦙 Ollama Local (Llama 3:8b - $0 Tokens)',
      rag_gemini_flash: '⚡ Gemini 3.6 Flash',
      rag_qdrant: '🔍 Qdrant (Similitud)',
      out_of_scope_llm: '🤖 Respuesta LLM (Fuera de Alcance)',
      fallback: '⚠️ Modo Fallback'
    };
    originBadge.innerText = originNames[meta.origen || ''] || meta.origen || '';
    metaBar.appendChild(originBadge);

    // Tiempo
    if (meta.tiempo_ms !== undefined) {
      const timeSpan = document.createElement('span');
      timeSpan.className = 'meta-time';
      timeSpan.innerText = `⏱️ ${meta.tiempo_ms.toFixed(1)} ms`;
      metaBar.appendChild(timeSpan);
    }

    // Escalamiento humano badge
    if (meta.escalar_humano) {
      const escBadge = document.createElement('span');
      escBadge.className = 'badge badge-escalar';
      escBadge.innerText = '👨‍💼 Escalar a Asesor Humano';
      metaBar.appendChild(escBadge);
    }

    msgDiv.appendChild(metaBar);

    // Citas documentales si existen
    if (meta.fuentes && meta.fuentes.length > 0) {
      const sourcesDetails = document.createElement('details');
      sourcesDetails.className = 'sources-container';
      const summary = document.createElement('summary');
      summary.innerText = `📚 ${meta.fuentes.length} Fuentes Oficiales Consultadas`;
      sourcesDetails.appendChild(summary);

      meta.fuentes.forEach((f) => {
        const item = document.createElement('div');
        item.className = 'source-item';
        item.innerHTML = `<strong>📄 ${f.documento}</strong> (Similitud: ${(f.score * 100).toFixed(1)}%)<p>${f.contenido}</p>`;
        sourcesDetails.appendChild(item);
      });
      msgDiv.appendChild(sourcesDetails);
    }
  }

  return msgDiv;
}

export function updateMetricsUI(metrics: MetricsResponse): void {
  const setEl = (id: string, val: string | number) => {
    const el = document.getElementById(id);
    if (el) el.innerText = String(val);
  };

  setEl('metric-total', metrics.consultas_totales);
  setEl('metric-cache', `${metrics.tasa_cache_hit_pct}% (${metrics.consultas_cache})`);
  setEl('metric-escalar', `${metrics.tasa_escalamiento_pct}% (${metrics.consultas_escaladas})`);
  setEl('metric-latency', `${metrics.latencia_promedio_ms} ms`);
  setEl('metric-cost', `$${metrics.costo_estimado_usd.toFixed(4)} USD`);
  setEl('metric-uptime', `${Math.floor(metrics.tiempo_actividad_segundos)}s`);
}
