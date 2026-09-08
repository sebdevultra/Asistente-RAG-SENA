"""
Pruebas de Base de Datos Vectorial Qdrant (Ingestión de 8 documentos y búsqueda de similitud).
"""

import pytest
from src.services.qdrant_service import qdrant_service
from src.config import settings

@pytest.mark.asyncio
async def test_ingestion_and_chunking_of_8_docs():
    res = await qdrant_service.ingest_documents()
    assert res["status"] == "success"
    assert res["documentos_procesados"] >= 8
    assert res["total_chunks"] >= 8


@pytest.mark.asyncio
async def test_qdrant_search_retrieval():
    # Asegurar ingestión
    if not qdrant_service.is_ready():
        await qdrant_service.ingest_documents()

    # Búsqueda sobre horarios
    results = await qdrant_service.search("horarios medellin jornada mañana", top_k=3)
    assert len(results) > 0
    assert any("01_horarios" in r["doc_name"] for r in results)
    assert results[0]["score"] > 0.0


@pytest.mark.asyncio
async def test_qdrant_search_pricing():
    # Búsqueda sobre precios y métodos de pago
    results = await qdrant_service.search("precio por nivel y descuento anual", top_k=3)
    assert len(results) > 0
    assert any("02_precios" in r["doc_name"] for r in results)
