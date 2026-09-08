"""
Motor de Orquestación RAG Multi-Tier:
1. Cache WAL (<2ms) -> Origen: 'cache'
2. Out-of-Scope -> Gemini responde amablemente sin escalar (escalar_humano: False, origen: 'out_of_scope_llm')
3. Scope Alto (similitud >= 0.40 en Qdrant) -> LLM Local Ollama (Llama 3, $0 tokens, origen: 'rag_ollama_local')
4. Scope Medio (0.20 <= similitud < 0.40) -> LLM Cloud Gemini 3.6 Flash (origen: 'rag_gemini_flash')
5. Contexto de Academia Insuficiente (similitud < 0.20) -> Escala a asesor humano (escalar_humano: True, origen: 'rag_qdrant')
"""

import time
import logging
from typing import List, Optional
from src.config import settings
from src.core.schemas import ChatResponse, ChatMessage, Citation
from src.core.constants import (
    SIMILARITY_LOCAL_LLM_THRESHOLD,
    SIMILARITY_ESCALATION_THRESHOLD,
    HUMAN_ESCALATION_MESSAGE,
    HUMAN_ESCALATION_KEYWORDS,
    SYSTEM_QUOTA_EXCEEDED_MESSAGE,
    OUT_OF_SCOPE_KEYWORDS,
    GREETING_KEYWORDS,
    GREETING_WELCOME_MESSAGE,
    CLASSIFY_INTENT_SYSTEM_PROMPT,
    SYSTEM_PROMPT_RAG,
)
from src.services.cache_service import cache_service
from src.services.qdrant_service import qdrant_service
from src.services.gemini_service import gemini_service
from src.services.ollama_service import ollama_service
from src.services.metrics_service import metrics_service

logger = logging.getLogger("rag_engine")

class RAGEngine:
    def __init__(self):
        pass

    def _is_greeting(self, query: str) -> bool:
        """
        Detecta saludos, despedidas y expresiones de cortesía bilingües.
        """
        clean = "".join(c for c in query.lower() if c.isalnum() or c.isspace()).strip()
        if not clean:
            return False
        tokens = clean.split()
        if len(tokens) <= 12:
            for kw in GREETING_KEYWORDS:
                if clean == kw or clean.startswith(kw) or clean.endswith(kw) or kw in clean:
                    return True
        return False

    def _is_out_of_scope(self, query: str) -> bool:
        """
        Detecta si la consulta es ajena al contexto de la academia de idiomas
        (recetas, programación, deportes, política, chistes, etc.).
        """
        q_lower = query.lower()
        for kw in OUT_OF_SCOPE_KEYWORDS:
            if kw in q_lower:
                return True
        return False

    def _needs_human_escalation(self, query: str) -> bool:
        """
        Detecta consultas administrativas complejas, casos médicos/fuerza mayor,
        incidentes transaccionales o solicitudes que requieren atención de asesor humano.
        """
        q_lower = query.lower()
        for kw in HUMAN_ESCALATION_KEYWORDS:
            if kw in q_lower:
                return True
        return False

    async def _classify_low_score_intent(self, query: str) -> str:
        """
        Clasifica consultas con baja similitud vectorial (< 0.20) para determinar
        si es un caso académico que requiere asesor humano (ACADEMIC_HUMAN)
        o si es una pregunta ajena que eludió las keywords (OUT_OF_SCOPE).
        """
        prompt = f"Consulta del usuario: \"{query}\"\nClasificación:"
        try:
            res = await gemini_service.generate_response(
                prompt=prompt,
                system_instruction=CLASSIFY_INTENT_SYSTEM_PROMPT
            )
            if res and "OUT_OF_SCOPE" in res.strip().upper():
                return "OUT_OF_SCOPE"
        except Exception as e:
            logger.warning(f"Error clasificando baja similitud: {e}")
        return "ACADEMIC_HUMAN"

    async def process_query(
        self,
        query: str,
        historial: Optional[List[ChatMessage]] = None
    ) -> ChatResponse:
        t_start = time.perf_counter()

        # 1. Compuerta FinOps: Verificación en Caché SQLite WAL (< 2ms)
        cached_data = await cache_service.get(query)
        if cached_data:
            t_ms = (time.perf_counter() - t_start) * 1000.0
            cached_data["tiempo_ms"] = round(t_ms, 2)
            cached_data["origen"] = "cache"
            response = ChatResponse(**cached_data)
            metrics_service.record_event("cache", response.escalar_humano, t_ms)
            return response

        # 2. Compuerta Nivel 1 Fast-Path: Saludos y Cortesías Bilingües (< 2ms)
        if self._is_greeting(query):
            t_ms = (time.perf_counter() - t_start) * 1000.0
            response = ChatResponse(
                respuesta=GREETING_WELCOME_MESSAGE,
                fuentes=[],
                confianza=1.0,
                escalar_humano=False,
                origen="chitchat_greeting",
                tiempo_ms=round(t_ms, 2)
            )
            await cache_service.set(query, response.model_dump())
            metrics_service.record_event("chitchat_greeting", False, t_ms)
            return response

        # 3. Compuerta Out-of-Scope (Palabras Clave Inmediatas):
        # Si NO tiene que ver con la academia, el LLM responde directamente (escalar_humano: False)
        if self._is_out_of_scope(query):
            prompt_out_of_scope = (
                f"El usuario pregunta: \"{query}\".\n"
                "Instrucción: Esta pregunta NO tiene que ver con la Academia Idiomas Colombia. "
                "Responde de forma amable, simpática y profesional con tono colombiano explicando que como asesora virtual "
                "tu especialidad es orientar sobre cursos de idiomas, horarios, precios, niveles, inscripciones y certificaciones, "
                "e invítale cordialmente a consultar sobre los programas de inglés. No inventes respuestas al tema ajeno."
            )
            try:
                llm_reply = await gemini_service.generate_response(
                    prompt=prompt_out_of_scope,
                    system_instruction=SYSTEM_PROMPT_RAG
                )
            except Exception:
                llm_reply = (
                    "¡Hola! Con mucho gusto te cuento que mi especialidad es orientarte en todo lo relacionado con "
                    "los programas de inglés, horarios, precios y matrículas de la Academia Idiomas Colombia. "
                    "¿Te gustaría conocer nuestros cursos o presentar una prueba de nivelación?"
                )

            t_ms = (time.perf_counter() - t_start) * 1000.0
            response = ChatResponse(
                respuesta=llm_reply,
                fuentes=[],
                confianza=0.90,
                escalar_humano=False,
                origen="out_of_scope_llm",
                tiempo_ms=round(t_ms, 2)
            )
            await cache_service.set(query, response.model_dump())
            metrics_service.record_event("out_of_scope_llm", False, t_ms)
            return response

        # 4. Consulta de Academia: Búsqueda en Qdrant
        if not qdrant_service.is_ready():
            await qdrant_service.ingest_documents()

        retrieved_chunks = await qdrant_service.search(query, top_k=3)
        max_score = max([c["score"] for c in retrieved_chunks], default=0.0)
        citations = [
            Citation(
                documento=c["doc_name"],
                contenido=c["text"][:280] + ("..." if len(c["text"]) > 280 else ""),
                score=c["score"]
            )
            for c in retrieved_chunks
        ]

        # 5. Compuerta Inteligente para Baja Similitud (Score < 0.20)
        if max_score < SIMILARITY_ESCALATION_THRESHOLD or not retrieved_chunks:
            intent = await self._classify_low_score_intent(query)
            if intent == "OUT_OF_SCOPE":
                prompt_out_of_scope = (
                    f"El usuario pregunta: \"{query}\".\n"
                    "Instrucción: Esta pregunta NO tiene que ver con la Academia Idiomas Colombia. "
                    "Responde de forma amable, simpática y profesional con tono colombiano explicando que como asesora virtual "
                    "tu especialidad es orientar sobre cursos de idiomas, horarios, precios, niveles, inscripciones y certificaciones, "
                    "e invítale cordialmente a consultar sobre los programas de inglés. No inventes respuestas al tema ajeno."
                )
                try:
                    llm_reply = await gemini_service.generate_response(
                        prompt=prompt_out_of_scope,
                        system_instruction=SYSTEM_PROMPT_RAG
                    )
                except Exception:
                    llm_reply = (
                        "¡Hola! Con mucho gusto te cuento que mi especialidad es orientarte en todo lo relacionado con "
                        "los programas de inglés, horarios, precios y matrículas de la Academia Idiomas Colombia. "
                        "¿Te gustaría conocer nuestros cursos o presentar una prueba de nivelación?"
                    )

                t_ms = (time.perf_counter() - t_start) * 1000.0
                response = ChatResponse(
                    respuesta=llm_reply,
                    fuentes=[],
                    confianza=0.85,
                    escalar_humano=False,
                    origen="out_of_scope_llm",
                    tiempo_ms=round(t_ms, 2)
                )
                await cache_service.set(query, response.model_dump())
                metrics_service.record_event("out_of_scope_llm", False, t_ms)
                return response

            # Si es ACADEMIC_HUMAN: Escalar formalmente al asesor humano
            t_ms = (time.perf_counter() - t_start) * 1000.0
            response = ChatResponse(
                respuesta=(
                    "Tu consulta está relacionada con nuestros servicios académicos, pero no encontré suficiente "
                    "información en los documentos autorizados para darte una respuesta completa o tu caso requiere "
                    "gestión personalizada de un asesor.\n\n"
                    f"{HUMAN_ESCALATION_MESSAGE}"
                ),
                fuentes=citations,
                confianza=round(max_score, 2),
                escalar_humano=True,
                origen="rag_qdrant",
                tiempo_ms=round(t_ms, 2)
            )
            await cache_service.set(query, response.model_dump())
            metrics_service.record_event("rag_qdrant", True, t_ms)
            return response

        # 5. Generación de Contexto Documental
        context_blocks = []
        for i, chunk in enumerate(retrieved_chunks, 1):
            context_blocks.append(
                f"--- [FRAGMENTO {i} | Fuente: {chunk['doc_name']} (Similitud: {chunk['score']})] ---\n"
                f"{chunk['text']}"
            )
        context_str = "\n\n".join(context_blocks)

        prompt_user = (
            f"[DOCUMENTACIÓN OFICIAL AUTORIZADA]:\n{context_str}\n\n"
            f"[PREGUNTA DEL ESTUDIANTE]:\n{query}\n\n"
            "Instrucción: Responde en español de forma amable y cálida siguiendo las políticas oficiales de la academia. "
            "Básate única y exclusivamente en los fragmentos anteriores."
        )

        resolved_origin = "rag_gemini_flash"
        llm_reply = None

        # 6. Enrutamiento Inteligente:
        # Si Ollama está habilitado y la similitud semántica es de Scope Alto (>= 0.40), usar LLM Local
        if settings.OLLAMA_ENABLED and max_score >= SIMILARITY_LOCAL_LLM_THRESHOLD:
            try:
                local_reply = await ollama_service.generate_response(
                    prompt=prompt_user,
                    system_instruction=SYSTEM_PROMPT_RAG
                )
                if local_reply:
                    llm_reply = local_reply
                    resolved_origin = "rag_ollama_local"
                    logger.info("Consulta resuelta exitosamente con LLM Local Ollama (Scope Alto).")
            except Exception as e:
                logger.warning(f"Fallo en Ollama local ({e}), aplicando fallback a Gemini Flash.")

        # Si no se usó Ollama o falló, usar Gemini 3.6 Flash
        if not llm_reply:
            try:
                llm_reply = await gemini_service.generate_response(
                    prompt=prompt_user,
                    system_instruction=SYSTEM_PROMPT_RAG
                )
                resolved_origin = "rag_gemini_flash"
            except Exception as e:
                err_msg = str(e).lower()
                logger.error(f"Error generando con Gemini: {e}")
                if "429" in err_msg or "resource_exhausted" in err_msg or "quota" in err_msg or "503" in err_msg or "unavailable" in err_msg:
                    llm_reply = SYSTEM_QUOTA_EXCEEDED_MESSAGE
                else:
                    llm_reply = (
                        "Estamos experimentando una intermitencia técnica temporal en el servicio de generación.\n\n"
                        f"{SYSTEM_QUOTA_EXCEEDED_MESSAGE}"
                    )
                resolved_origin = "fallback"

        # Detectar si el caso requiere derivación o escalamiento formal a asesor humano
        needs_escalation = self._needs_human_escalation(query)
        if needs_escalation:
            reply_lower = (llm_reply or "").lower()
            if "whatsapp" not in reply_lower and "asesor" not in reply_lower:
                llm_reply = (
                    f"{llm_reply}\n\n"
                    f"Para gestionar este trámite específico con el equipo administrativo y académico:\n"
                    f"{HUMAN_ESCALATION_MESSAGE}"
                )
            elif "whatsapp" not in reply_lower:
                llm_reply = f"{llm_reply}\n\n{HUMAN_ESCALATION_MESSAGE}"

        t_ms = (time.perf_counter() - t_start) * 1000.0
        final_conf = min(0.99, max(0.50, round(max_score, 2)))

        response = ChatResponse(
            respuesta=llm_reply or "¡Con gusto te oriento con la información de nuestros programas académicos!",
            fuentes=citations,
            confianza=final_conf,
            escalar_humano=bool(needs_escalation),
            origen=resolved_origin,
            tiempo_ms=round(t_ms, 2)
        )

        if resolved_origin not in ["fallback"] and not (llm_reply and "límite de cuota" in llm_reply):
            await cache_service.set(query, response.model_dump())
        metrics_service.record_event(resolved_origin, bool(needs_escalation), t_ms)
        return response


# Instancia singleton
rag_engine = RAGEngine()
