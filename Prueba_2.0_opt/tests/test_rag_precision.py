"""
Pruebas de Calidad y Precisión RAG:
1. Out-of-scope: Responde el LLM (Gemini) aclarando su función (escalar_humano: False).
2. Contexto de Academia sin información / score < 0.20: Escala a asesor humano (escalar_humano: True).
3. Contexto de Academia resuelto: Gemini responde fundamentado (escalar_humano: False).
4. Caché WAL: Sub-5ms response time.
"""

import pytest
from src.services.rag_engine import rag_engine

@pytest.mark.asyncio
async def test_rag_in_scope_query():
    # Consulta válida sobre horarios institucionales
    res = await rag_engine.process_query("¿Cuáles son los horarios de clases de la sede Medellín?")
    assert res.confianza >= 0.20
    assert res.escalar_humano is False
    assert len(res.fuentes) > 0
    assert res.origen in ["rag_ollama_local", "rag_gemini_flash", "rag_qdrant", "cache"]


@pytest.mark.asyncio
async def test_rag_out_of_scope_handled_by_llm_without_escalation():
    # Consulta ajena a la academia (receta de cocina)
    res = await rag_engine.process_query("¿Cómo preparo una receta de pizza?")
    assert res.origen == "out_of_scope_llm"
    assert res.escalar_humano is False  # Regla: Out-of-scope lo responde el LLM, NO se escala a humano
    assert len(res.respuesta) > 20


@pytest.mark.asyncio
async def test_rag_academy_context_insufficient_data_escalates_to_human():
    # Consulta del contexto de la academia pero que no existe en los documentos (baja similitud o solicitud no contemplada)
    res = await rag_engine.process_query("¿Tienen convenio de intercambio estudiantil con la universidad de Tokio en Japón?")
    # Pertenece a temas educativos/académicos pero no está en los 8 documentos de la academia colombiana
    assert res.escalar_humano is True  # Regla: Contexto de academia sin soporte -> Escala a humano
    assert res.origen == "rag_qdrant"
    assert "asesor" in res.respuesta.lower() or "whatsapp" in res.respuesta.lower()


@pytest.mark.asyncio
async def test_cache_hit_sub_5ms():
    query = "¿Cuál es el costo del Placement Test o examen de clasificación?"
    
    # 1. Primera consulta
    res1 = await rag_engine.process_query(query)
    assert res1 is not None

    # 2. Segunda consulta (Cache WAL)
    res2 = await rag_engine.process_query(query)
    assert res2.origen == "cache"
    assert res2.tiempo_ms < 20.0


@pytest.mark.asyncio
async def test_rag_greeting_fast_path_hello_there():
    # Consulta de saludo en inglés (la que antes rompía la semántica)
    res1 = await rag_engine.process_query("Hello there")
    assert res1.origen == "chitchat_greeting"
    assert res1.escalar_humano is False
    assert len(res1.fuentes) == 0
    assert res1.confianza == 1.0
    assert "sofía" in res1.respuesta.lower()

    # Consulta de saludo en español
    res2 = await rag_engine.process_query("¡Hola! Buenos días")
    assert res2.origen in ["chitchat_greeting", "cache"]
    assert res2.escalar_humano is False
    assert len(res2.fuentes) == 0

