"""
Pruebas automatizadas de API Backend (FastAPI, Endpoints, Validación de Esquemas y Seguridad).
"""

import pytest
from fastapi.testclient import TestClient
from src.main import app
from src.config import settings

client = TestClient(app)

def test_health_check_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "Gemini" in data["llm_model"] or "gemini" in data["llm_model"].lower()
    assert data["cache_engine"] == "SQLite WAL"


def test_metrics_endpoint():
    response = client.get("/api/metrics")
    assert response.status_code == 200
    data = response.json()
    assert "consultas_totales" in data
    assert "tasa_cache_hit_pct" in data
    assert "tasa_escalamiento_pct" in data
    assert "latencia_promedio_ms" in data


def test_chat_endpoint_validation_error():
    # Pregunta vacía debe retornar error 422 Unprocessable Entity
    response = client.post("/api/chat", json={"pregunta": ""})
    assert response.status_code == 422


def test_admin_ingest_unauthorized():
    # Sin clave de administrador debe rechazar 401
    response = client.post("/api/ingest")
    assert response.status_code == 401


def test_admin_ingest_authorized():
    # Con clave correcta debe procesar los 8 documentos
    response = client.post(
        "/api/ingest",
        headers={"X-Admin-Key": settings.ADMIN_API_KEY}
    )
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert data["documentos_procesados"] >= 8
    assert data["total_chunks"] > 0
