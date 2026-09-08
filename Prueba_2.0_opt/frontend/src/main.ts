/**
 * Controlador principal de la interfaz interactiva en TypeScript.
 */

import { sendChatMessage, fetchMetrics, triggerIngestion } from './api';
import { createMessageElement, updateMetricsUI } from './ui';
import { ChatMessage } from './types';

const chatHistory: ChatMessage[] = [];

document.addEventListener('DOMContentLoaded', () => {
  const chatMessagesEl = document.getElementById('chat-messages') as HTMLDivElement;
  const chatInput = document.getElementById('chat-input') as HTMLInputElement;
  const sendBtn = document.getElementById('send-btn') as HTMLButtonElement;
  const reingestBtn = document.getElementById('reingest-btn') as HTMLButtonElement;
  const adminKeyInput = document.getElementById('admin-key-input') as HTMLInputElement;
  const chips = document.querySelectorAll('.chip');

  // Polling de métricas cada 4 segundos
  async function refreshMetrics() {
    try {
      const metrics = await fetchMetrics();
      updateMetricsUI(metrics);
    } catch {
      // Ignorar fallos de red transitorios en polling
    }
  }
  refreshMetrics();
  setInterval(refreshMetrics, 4000);

  // Manejar envío de preguntas
  async function handleSend(questionText?: string) {
    const text = (questionText || chatInput.value).trim();
    if (!text) return;

    chatInput.value = '';
    chatInput.disabled = true;
    sendBtn.disabled = true;

    // Agregar mensaje del usuario al DOM
    const userMsg = createMessageElement('user', text);
    chatMessagesEl.appendChild(userMsg);
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;

    chatHistory.push({ role: 'user', content: text });

    // Mensaje de carga temporal
    const loadingMsg = document.createElement('div');
    loadingMsg.className = 'message assistant-message loading-indicator';
    loadingMsg.innerText = '🔍 Consultando Qdrant & Gemini 3.6 Flash...';
    chatMessagesEl.appendChild(loadingMsg);
    chatMessagesEl.scrollTop = chatMessagesEl.scrollHeight;

    try {
      const response = await sendChatMessage({
        pregunta: text,
        historial: chatHistory.slice(-4), // Mantener contexto multi-turno
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

      // Actualizar telemetría inmediatamente
      refreshMetrics();
    } catch (err: unknown) {
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

  // Event Listeners
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

  // Re-ingestión administrativa
  if (reingestBtn) {
    reingestBtn.addEventListener('click', async () => {
      const key = adminKeyInput.value.trim() || 'admin-super-secret-key-2026';
      reingestBtn.disabled = true;
      reingestBtn.innerText = '⏳ Indexando...';
      try {
        const res = await triggerIngestion(key);
        alert(`✅ Ingestión exitosa: ${res.documentos_procesados} documentos y ${res.total_chunks} chunks indexados en ${res.tiempo_ms}ms.`);
      } catch (err: unknown) {
        const msg = err instanceof Error ? err.message : 'Fallo en ingestión';
        alert(`❌ Error en ingestión: ${msg}`);
      } finally {
        reingestBtn.disabled = false;
        reingestBtn.innerText = '🔄 Re-indexar Documentos';
      }
    });
  }
});
