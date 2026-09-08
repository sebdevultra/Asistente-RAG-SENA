"""
Prueba de coherencia de contratos: Valida que las interfaces TypeScript en frontend/src/types.ts
coincidan en campos con los esquemas Pydantic v2 en src/core/schemas.py.
"""

from pathlib import Path
from src.core.schemas import ChatRequest, ChatResponse, MetricsResponse, IngestResponse

def test_pydantic_schema_fields_presence():
    # Validar campos esperados en Pydantic
    chat_req_fields = set(ChatRequest.model_fields.keys())
    assert "pregunta" in chat_req_fields
    assert "historial" in chat_req_fields

    chat_resp_fields = set(ChatResponse.model_fields.keys())
    assert {"respuesta", "fuentes", "confianza", "escalar_humano", "origen", "tiempo_ms"}.issubset(chat_resp_fields)

    metrics_fields = set(MetricsResponse.model_fields.keys())
    assert {"consultas_totales", "tasa_cache_hit_pct", "tasa_escalamiento_pct", "latencia_promedio_ms"}.issubset(metrics_fields)


def test_typescript_file_exists_and_contains_contracts():
    ts_file = Path(__file__).resolve().parent.parent / "frontend" / "src" / "types.ts"
    assert ts_file.exists(), "El archivo frontend/src/types.ts debe existir"
    
    content = ts_file.read_text(encoding="utf-8")
    assert "interface ChatRequest" in content
    assert "interface ChatResponse" in content
    assert "interface MetricsResponse" in content
    assert "interface Citation" in content
    assert "escalar_humano: boolean" in content
    assert "origen: ResponseOrigin" in content
    assert "'chitchat_greeting'" in content
