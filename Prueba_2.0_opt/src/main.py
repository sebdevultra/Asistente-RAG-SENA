"""
Punto de entrada principal de la API FastAPI para el Asistente Virtual RAG.
Expone endpoints asíncronos y sirve la interfaz Web interactiva.
"""

import time
import logging
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI, HTTPException, Header, Depends, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from src.config import settings
from src.core.schemas import (
    ChatRequest,
    ChatResponse,
    MetricsResponse,
    IngestResponse,
)
from src.services.rag_engine import rag_engine
from src.services.metrics_service import metrics_service
from src.services.qdrant_service import qdrant_service
from src.services.cache_service import cache_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s"
)
logger = logging.getLogger("api_main")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Iniciar worker de telemetría y preparar base vectorial
    logger.info("Iniciando servicio Asistente Virtual RAG con Qdrant...")
    await metrics_service.start_worker()
    try:
        if not qdrant_service.is_ready():
            logger.info("Qdrant no inicializado. Iniciando ingestión automática de los 8 documentos...")
            await qdrant_service.ingest_documents()
    except Exception as e:
        logger.error(f"Error durante el warmup de Qdrant: {e}")
    yield
    # Shutdown
    logger.info("Deteniendo servicio Asistente Virtual RAG...")


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="API Asíncrona de Alto Rendimiento para Atención al Cliente con Qdrant y Gemini 3.6 Flash",
    lifespan=lifespan
)

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Dependencia de seguridad para rutas administrativas
def verify_admin_key(x_admin_key: str = Header(None)):
    if not x_admin_key or x_admin_key != settings.ADMIN_API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Clave de administrador (X-Admin-Key) inválida o no provista"
        )
    return True


@app.post(
    "/api/chat",
    response_model=ChatResponse,
    summary="Procesar consulta de usuario vía RAG",
    tags=["Chat"]
)
async def chat_endpoint(request: ChatRequest):
    """
    Procesa una pregunta utilizando el pipeline optimizado de 4 capas:
    1. Fast-Path Out-of-Scope (<1ms)
    2. Caché SQLite WAL (<2ms)
    3. Búsqueda Vectorial Qdrant (Top-3 Chunks)
    4. Generación Fundamentada con Gemini 3.6 Flash / Escalamiento Humano (Umbral < 0.20)
    """
    try:
        response = await rag_engine.process_query(
            query=request.pregunta,
            historial=request.historial
        )
        return response
    except Exception as e:
        logger.error(f"Error procesando chat: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error interno procesando la consulta: {str(e)}"
        )


@app.get(
    "/api/metrics",
    response_model=MetricsResponse,
    summary="Obtener métricas y telemetría FinOps",
    tags=["Observabilidad"]
)
async def get_metrics():
    """
    Retorna métricas en tiempo real: consultas atendidas, tasa de caché,
    tasa de escalamiento a humano, latencia promedio y costo estimado.
    """
    return metrics_service.get_metrics()


@app.post(
    "/api/ingest",
    response_model=IngestResponse,
    summary="Re-indexar los 8 documentos en Qdrant",
    tags=["Administración"]
)
async def ingest_documents_endpoint(authorized: bool = Depends(verify_admin_key)):
    """
    Lee los 8 documentos de negocio en docs/, calcula embeddings vectoriales
    y regenera la colección en Qdrant.
    """
    t_start = time.perf_counter()
    try:
        res = await qdrant_service.ingest_documents()
        await cache_service.clear()  # Invalidar caché para evitar inconsistencias
        t_ms = (time.perf_counter() - t_start) * 1000.0
        return IngestResponse(
            status="success",
            documentos_procesados=res["documentos_procesados"],
            total_chunks=res["total_chunks"],
            tiempo_ms=round(t_ms, 2)
        )
    except Exception as e:
        logger.error(f"Error en ingestión: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Fallo en la indexación de documentos: {str(e)}"
        )


@app.get(
    "/api/health",
    summary="Verificar estado de salud del sistema",
    tags=["Sistema"]
)
async def health_check():
    return {
        "status": "healthy",
        "version": settings.VERSION,
        "llm_model": settings.GEMINI_MODEL,
        "embedding_model": settings.GEMINI_EMBEDDING_MODEL,
        "vector_store": "Qdrant (Local Embedded)",
        "cache_engine": "SQLite WAL",
        "vector_store_ready": qdrant_service.is_ready()
    }


# Montar Frontend estático
frontend_dir = Path(__file__).resolve().parent.parent / "frontend"
if (frontend_dir / "index.html").exists():
    app.mount("/static", StaticFiles(directory=str(frontend_dir)), name="static")

    @app.get("/")
    async def serve_index():
        return FileResponse(frontend_dir / "index.html")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("src.main:app", host=settings.HOST, port=settings.PORT, reload=True)
