"""
Servicio de integración con LLM Local Ollama (Llama 3 / Llama 3.2).
Procesa consultas de scope alto (similitud >= 0.40) con costo $0 en tokens y baja latencia local.
"""

import logging
from typing import Optional
import httpx
from src.config import settings

logger = logging.getLogger("ollama_service")

class OllamaService:
    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL.rstrip("/")
        self.model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT_SECONDS

    async def is_available(self) -> bool:
        """Verifica si el demonio local de Ollama está activo y respondiendo."""
        try:
            async with httpx.AsyncClient(timeout=2.0) as client:
                res = await client.get(f"{self.base_url}/api/tags")
                return res.status_code == 200
        except Exception:
            return False

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> Optional[str]:
        """
        Envía una solicitud de generación al modelo local de Ollama.
        Retorna el texto generado o None si Ollama no responde (para activar fallback a Gemini).
        """
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.2,
                "top_p": 0.9,
            }
        }
        if system_instruction:
            payload["system"] = system_instruction

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                res = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload
                )
                if res.status_code == 200:
                    data = res.json()
                    return data.get("response", "").strip()
                else:
                    logger.warning(f"Ollama respondió con código {res.status_code}: {res.text}")
                    return None
        except (httpx.TimeoutException, httpx.ReadTimeout):
            logger.info(f"Ollama local superó el timeout de {self.timeout}s. Aplicando fallback inmediato a Gemini Flash.")
            return None
        except httpx.ConnectError:
            logger.info("Ollama no está en ejecución local (puerto 11434 inalcanzable). Se aplicará fallback a Gemini Flash.")
            return None
        except Exception as e:
            logger.warning(f"Error comunicando con Ollama local: {e}")
            return None


# Instancia singleton
ollama_service = OllamaService()
