"""
Modelos y contratos de datos Pydantic v2 para el Asistente Virtual RAG.
Garantiza tipado estricto y validación de entrada/salida para la API.
"""

from typing import List, Optional, Literal
from pydantic import BaseModel, Field, field_validator


class ChatMessage(BaseModel):
    role: Literal["user", "assistant", "system"] = Field(
        ..., description="Rol del emisor del mensaje"
    )
    content: str = Field(..., min_length=1, description="Contenido textual del mensaje")


class ChatRequest(BaseModel):
    pregunta: str = Field(
        ...,
        min_length=2,
        max_length=1000,
        description="Consulta formulada por el estudiante o aspirante",
        examples=["¿Cuáles son los horarios de clase en la sede Medellín?"],
    )
    historial: Optional[List[ChatMessage]] = Field(
        default=[],
        description="Historial previo de la conversación para contexto multi-turno",
    )

    @field_validator("pregunta")
    @classmethod
    def sanitizar_pregunta(cls, v: str) -> str:
        clean = v.strip()
        if not clean:
            raise ValueError("La pregunta no puede estar vacía o contener solo espacios")
        return clean


class Citation(BaseModel):
    documento: str = Field(..., description="Nombre del archivo o identificador del documento fuente")
    contenido: str = Field(..., description="Fragmento de texto (chunk) recuperado")
    score: float = Field(..., ge=0.0, le=1.0, description="Puntuación de similitud coseno Qdrant")


class ChatResponse(BaseModel):
    respuesta: str = Field(..., description="Respuesta final generada para el usuario")
    fuentes: List[Citation] = Field(
        default=[], description="Citas y fragmentos documentales utilizados"
    )
    confianza: float = Field(
        ..., ge=0.0, le=1.0, description="Nivel de confianza en la respuesta generada"
    )
    escalar_humano: bool = Field(
        ..., description="True solo si la consulta pertenece al contexto de la academia pero requiere asesor humano"
    )
    origen: Literal[
        "cache",
        "chitchat_greeting",
        "rag_ollama_local",
        "rag_gemini_flash",
        "rag_qdrant",
        "out_of_scope_llm",
        "fallback"
    ] = Field(
        ..., description="Capa del sistema que resolvió la petición"
    )
    tiempo_ms: float = Field(
        ..., ge=0.0, description="Tiempo total de procesamiento en milisegundos"
    )


class MetricsResponse(BaseModel):
    consultas_totales: int = Field(..., description="Total de consultas procesadas")
    consultas_cache: int = Field(..., description="Consultas resueltas desde caché WAL")
    consultas_rag: int = Field(..., description="Consultas resueltas vía RAG (Ollama / Gemini)")
    consultas_escaladas: int = Field(..., description="Consultas derivadas a asesores humanos (contexto de academia)")
    tasa_cache_hit_pct: float = Field(..., description="Porcentaje de acierto de caché")
    tasa_escalamiento_pct: float = Field(..., description="Porcentaje de consultas escaladas a humano")
    latencia_promedio_ms: float = Field(..., description="Latencia promedio general en ms")
    costo_estimado_usd: float = Field(..., description="Costo estimado en USD por tokens")
    tiempo_actividad_segundos: float = Field(..., description="Tiempo de actividad del servicio")


class IngestResponse(BaseModel):
    status: str = Field(..., description="Estado de la operación de ingestión")
    documentos_procesados: int = Field(..., description="Número de documentos leídos")
    total_chunks: int = Field(..., description="Total de fragmentos indexados en Qdrant")
    tiempo_ms: float = Field(..., description="Tiempo de indexación en milisegundos")
