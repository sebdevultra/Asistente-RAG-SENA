/**
 * Bundle compilado desde TypeScript (src/api.ts, src/ui.ts, src/main.ts).
 * Integrado con Qdrant y Gemini 3.6 Flash.
 */

const API_BASE = '';

async function sendChatMessage(request) {
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

async function fetchMetrics() {
  const response = await fetch(`${API_BASE}/api/metrics`);
  if (!response.ok) {
    throw new Error(`Error obteniendo métricas: ${response.statusText}`);
  }
  return response.json();
}

async function triggerIngestion(adminKey) {
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

function createMessageElement(sender, text, meta) {
  const msgDiv = document.createElement('div');
  msgDiv.className = `message ${sender}-message`;

  const contentDiv = document.createElement('div');
  contentDiv.className = 'message-content';
  contentDiv.innerText = text;
  msgDiv.appendChild(contentDiv);

  if (meta && sender === 'assistant') {
    const metaBar = document.createElement('div');
    metaBar.className = 'message-meta';

    const originBadge = document.createElement('span');
    originBadge.className = `badge origin-${meta.origen || 'unknown'}`;
    const originNames = {
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

    if (meta.tiempo_ms !== undefined) {
      const timeSpan = document.createElement('span');
      timeSpan.className = 'meta-time';
      timeSpan.innerText = `⏱️ ${meta.tiempo_ms.toFixed(1)} ms`;
      metaBar.appendChild(timeSpan);
    }

    if (meta.escalar_humano) {
      const escBadge = document.createElement('span');
      escBadge.className = 'badge badge-escalar';
      escBadge.innerText = '👨‍💼 Escalar a Asesor Humano';
      metaBar.appendChild(escBadge);
    }

    msgDiv.appendChild(metaBar);

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

function updateMetricsUI(metrics) {
  const setEl = (id, val) => {
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

const chatHistory = [];

document.addEventListener('DOMContentLoaded', () => {
  const chatMessagesEl = document.getElementById('chat-messages');
  const chatInput = document.getElementById('chat-input');
  const sendBtn = document.getElementById('send-btn');
  const reingestBtn = document.getElementById('reingest-btn');
  const adminKeyInput = document.getElementById('admin-key-input');
  const chips = document.querySelectorAll('.chip');

  async function refreshMetrics() {
    try {
      const metrics = await fetchMetrics();
      updateMetricsUI(metrics);
    } catch {
      // Ignorar errores de polling
    }
  }
  refreshMetrics();
  setInterval(refreshMetrics, 4000);

  async function handleSend(questionText) {
    const text = (questionText || chatInput.value).trim();
    if (!text) return;

    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    const userMsg = createMessageElement('user', text);
    chatMessagesEl.appendChild(userMsg);
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;

    chatHistory.push({ role: 'user', content: text });

    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message assistant-message loading-indicator';
    loadingMsg.innerText = '🔍 Consultando Qdrant & Gemini 3.6 Flash...';
    chatMessagesEl.appendChild(loadingMsg);
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;

    try {
      const response = await sendChatMessage({
        pregunta: text,
        historial: chatHistory.slice(-4),
      });

      loadingMsg.remove();

      const assistantMsg = createMessageElement('assistant', response.respuesta, {
        tiempo_ms: response.tiempo_ms,
        origen: response.origen,
        confianza: response.confianza,
        escalar_humano: response.escalar_humano,
        fuentes: response.fuentes,
      });

      chatMessagesEl.appendChild(assistantMsg);
      chatHistory.push({ role: 'assistant', content: response.respuesta });
      chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;

      refreshMetrics();
    } catch (err) {
      loadingMsg.remove();
      const errText = err instanceof Error ? err.message : 'Error inesperado';
      const errorDiv = createMessageElement('assistant', `❌ Error: ${errText}`);
      chatMessagesEl.appendChild(errorDiv);
      chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;
    } finally {
      chatInput.disabled = false;
      sendBtn.disabled = false;
      chatInput.focus();
    }
  }

  sendBtn.addEventListener('click', () => handleSend());
  chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      handleSend();
    }
  });

  chips.forEach((chip) => {
    chip.addEventListener('click', () => {
      const text = chip.getAttribute('data-query');
      if (text) handleSend(text);
    });
  });

  if (reingestBtn) {
    reingestBtn.addEventListener('click', async () => {
      const key = adminKeyInput.value.trim() || 'admin-super-secret-key-2026';
      reingestBtn.disabled = true;
      reingestBtn.innerText = '⏳ Indexando...';
      try {
        const res = await triggerIngestion(key);
        alert(`✅ Ingestión exitosa en Qdrant: ${res.documentos_procesados} documentos y ${res.total_chunks} chunks indexados en ${res.tiempo_ms}ms.`);
      } catch (err) {
        const msg = err instanceof Error ? err.message : 'Fallo en ingestión';
        alert(`❌ Error en ingestión: ${msg}`);
      } finally {
        reingestBtn.disabled = false;
        reingestBtn.innerText = '🔄 Re-indexar 8 Documentos';
      }
    });
  }
});
