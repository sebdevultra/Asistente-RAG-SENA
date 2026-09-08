"""
Servicio de integración con la API de Google Gemini (Gemini 3.6 Flash y Embeddings).
Maneja la generación de contenido fundamentado y la vectorización de textos.
"""

import os
import asyncio
import logging
from typing import List, Optional
from src.config import settings

logger = logging.getLogger("gemini_service")

class GeminiService:
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.model_name = settings.GEMINI_MODEL
        self.embedding_model = settings.GEMINI_EMBEDDING_MODEL
        self._client = None
        self._init_client()

    def _init_client(self):
        if not self.api_key:
            logger.warning("GEMINI_API_KEY no configurada. El servicio operará en modo simulado/mock.")
            return

        # Protección FinOps: Si se ejecutan pruebas automatizadas (pytest), no consumir tokens de la cuenta
        import sys
        if "pytest" in sys.modules or any("pytest" in arg for arg in sys.argv) or os.getenv("PYTEST_CURRENT_TEST") or settings.ENVIRONMENT == "test":
            logger.info("Modo de pruebas detectado: Gemini operará en modo offline determinista para no consumir tokens.")
            self._client = None
            return

        try:
            from google import genai
            self._client = genai.Client(api_key=self.api_key)
            logger.info(f"Cliente Gemini inicializado con modelo {self.model_name}")
        except Exception as e:
            logger.error(f"Error inicializando google-genai client: {e}")
            self._client = None

    async def generate_embedding(self, text: str) -> List[float]:
        """
        Genera el vector de embedding para un texto dado usando text-embedding-004.
        """
        if not self._client:
            # Feature hashing semántico normalizado (excluyendo stop words para evitar inflación de scores)
            import math
            stop_words = {
                "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
                "un", "para", "con", "no", "una", "su", "al", "lo", "como", "mas", "pero",
                "sus", "le", "ya", "o", "este", "si", "porque", "esta", "entre", "cuando",
                "muy", "sin", "sobre", "tambien", "me", "hasta", "hay", "donde", "quien",
                "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra",
                "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mi", "antes", "unos",
                "yo", "otro", "otras", "otra", "tanto", "esa", "estos", "mucho", "quienes",
                "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo",
                "es", "son", "tienen", "tiene", "puedo"
            }
            words = text.lower().split()
            vec = [0.0] * 768
            for w in words:
                clean = "".join(c for c in w if c.isalnum())
                if clean and clean not in stop_words and len(clean) > 2:
                    # Normalización de plurales en español para emular similitud sub-léxica
                    if clean.endswith("es") and len(clean) > 4:
                        clean = clean[:-2]
                    elif clean.endswith("s") and len(clean) > 3:
                        clean = clean[:-1]
                    idx = abs(hash(clean)) % 768
                    vec[idx] += 1.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            return [x / norm for x in vec]

        def _sync_embed():
            from google.genai import types
            from google import genai
            config = types.EmbedContentConfig(output_dimensionality=768)
            keys_to_try = [self.api_key] + [k for k in getattr(settings, "GEMINI_BACKUP_KEYS", []) if k != self.api_key]
            last_err = None
            for key in keys_to_try:
                try:
                    client = self._client if key == self.api_key and self._client else genai.Client(
                        api_key=key,
                        http_options=types.HttpOptions(timeout=10000)
                    )
                    response = client.models.embed_content(
                        model=self.embedding_model,
                        contents=text,
                        config=config
                    )
                    if key != self.api_key:
                        self.api_key = key
                        self._client = client
                        logger.info(f"Embeddings: Rotado con éxito a clave {key[:10]}...")
                    if hasattr(response, "embedding") and hasattr(response.embedding, "values"):
                        return list(response.embedding.values)
                    elif hasattr(response, "embeddings") and len(response.embeddings) > 0:
                        return list(response.embeddings[0].values)
                    raise ValueError("No se pudo extraer el vector de embedding de la respuesta")
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(x in err_s for x in ["429", "503", "unavailable", "resource_exhausted", "quota", "timed out", "timeout"]):
                        logger.warning(f"Clave {key[:10]} indisponible ({ex}), probando respaldo...")
                        continue
                    raise ex
            raise last_err

        try:
            return await asyncio.to_thread(_sync_embed)
        except Exception as e:
            logger.error(f"Error generando embedding con Gemini: {e}")
            import math
            stop_words = {
                "de", "la", "que", "el", "en", "y", "a", "los", "del", "se", "las", "por",
                "un", "para", "con", "no", "una", "su", "al", "lo", "como", "mas", "pero",
                "sus", "le", "ya", "o", "este", "si", "porque", "esta", "entre", "cuando",
                "muy", "sin", "sobre", "tambien", "me", "hasta", "hay", "donde", "quien",
                "desde", "todo", "nos", "durante", "todos", "uno", "les", "ni", "contra",
                "otros", "ese", "eso", "ante", "ellos", "e", "esto", "mi", "antes", "unos",
                "yo", "otro", "otras", "otra", "tanto", "esa", "estos", "mucho", "quienes",
                "nada", "muchos", "cual", "poco", "ella", "estar", "estas", "algunas", "algo",
                "es", "son", "tienen", "tiene", "puedo"
            }
            words = text.lower().split()
            vec = [0.0] * 768
            for w in words:
                clean = "".join(c for c in w if c.isalnum())
                if clean and clean not in stop_words and len(clean) > 2:
                    if clean.endswith("es") and len(clean) > 4:
                        clean = clean[:-2]
                    elif clean.endswith("s") and len(clean) > 3:
                        clean = clean[:-1]
                    idx = abs(hash(clean)) % 768
                    vec[idx] += 1.0
            norm = math.sqrt(sum(x * x for x in vec)) or 1.0
            return [x / norm for x in vec]

    async def generate_response(
        self,
        prompt: str,
        system_instruction: Optional[str] = None
    ) -> str:
        """
        Genera una respuesta con Gemini 3.6 Flash de forma asíncrona.
        """
        if not self._client and not getattr(settings, "GEMINI_BACKUP_KEYS", []):
            return (
                "Esta es una respuesta simulada del Asistente Virtual (Gemini 3.6 Flash) "
                "porque no se ha configurado la variable GEMINI_API_KEY en el entorno."
            )

        from google.genai import types
        from google import genai

        def _sync_generate():
            config = types.GenerateContentConfig(
                temperature=settings.GEMINI_TEMPERATURE,
                top_p=0.9,
                system_instruction=system_instruction if system_instruction else None
            )
            keys_to_try = [self.api_key] + [k for k in getattr(settings, "GEMINI_BACKUP_KEYS", []) if k != self.api_key]
            last_err = None
            for key in keys_to_try:
                try:
                    client = self._client if key == self.api_key and self._client else genai.Client(
                        api_key=key,
                        http_options=types.HttpOptions(timeout=10000)
                    )
                    response = client.models.generate_content(
                        model=self.model_name,
                        contents=prompt,
                        config=config
                    )
                    if key != self.api_key:
                        self.api_key = key
                        self._client = client
                        logger.info(f"Generación: Rotado con éxito a clave {key[:10]}...")
                    return response.text.strip() if response and response.text else ""
                except Exception as ex:
                    last_err = ex
                    err_s = str(ex).lower()
                    if any(x in err_s for x in ["429", "503", "unavailable", "resource_exhausted", "quota", "timed out", "timeout"]):
                        logger.warning(f"Clave {key[:10]} indisponible ({ex}), probando respaldo...")
                        continue
                    raise ex
            raise last_err

        try:
            return await asyncio.to_thread(_sync_generate)
        except Exception as e:
            logger.error(f"Error invocando Gemini Flash {self.model_name}: {e}")
            raise e


# Instancia singleton del servicio
gemini_service = GeminiService()
