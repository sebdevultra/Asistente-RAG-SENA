"""
Servicio de métricas y telemetría no bloqueante basado en cola asíncrona.
Calcula métricas FinOps: consultas procesadas, tasa de caché, tasa de escalamiento y latencias.
"""

import asyncio
import time
from typing import Dict, Any, List
from src.core.schemas import MetricsResponse

class MetricsService:
    def __init__(self):
        self.start_time = time.time()
        self.total_queries = 0
        self.cache_hits = 0
        self.rag_queries = 0
        self.escalated_queries = 0
        self.latencies_ms: List[float] = []
        self._queue: asyncio.Queue = asyncio.Queue()
        self._worker_task: asyncio.Task = None

    async def start_worker(self):
        """Inicia el worker en segundo plano para procesar eventos de telemetría."""
        if self._worker_task is None or self._worker_task.done():
            self._worker_task = asyncio.create_task(self._process_queue())

    async def _process_queue(self):
        while True:
            event = await self._queue.get()
            try:
                self.total_queries += 1
                origin = event.get("origin")
                escalar = event.get("escalar_humano", False)
                latency = event.get("tiempo_ms", 0.0)

                if origin == "cache":
                    self.cache_hits += 1
                else:
                    self.rag_queries += 1

                if escalar:
                    self.escalated_queries += 1

                self.latencies_ms.append(latency)
                # Mantener solo las últimas 1000 latencias en memoria
                if len(self.latencies_ms) > 1000:
                    self.latencies_ms.pop(0)

            except Exception:
                pass
            finally:
                self._queue.task_done()

    def record_event(self, origin: str, escalar_humano: bool, tiempo_ms: float):
        """Encola un evento de telemetría sin bloquear el hilo principal."""
        try:
            self._queue.put_nowait({
                "origin": origin,
                "escalar_humano": escalar_humano,
                "tiempo_ms": tiempo_ms
            })
        except Exception:
            # Fallback síncrono si la cola estuviera llena
            self.total_queries += 1
            if origin == "cache":
                self.cache_hits += 1
            else:
                self.rag_queries += 1
            if escalar_humano:
                self.escalated_queries += 1
            self.latencies_ms.append(tiempo_ms)

    def get_metrics(self) -> MetricsResponse:
        total = self.total_queries
        cache_pct = (self.cache_hits / total * 100.0) if total > 0 else 0.0
        esc_pct = (self.escalated_queries / total * 100.0) if total > 0 else 0.0
        avg_latency = (sum(self.latencies_ms) / len(self.latencies_ms)) if self.latencies_ms else 0.0
        uptime = time.time() - self.start_time

        # Costo aproximado Gemini Flash: ~$0.000075 por 1k tokens de entrada y $0.00030 por 1k tokens de salida
        # Estimamos un promedio de 800 tokens por consulta RAG y 0 para caché
        estimated_cost = self.rag_queries * 0.00025

        return MetricsResponse(
            consultas_totales=total,
            consultas_cache=self.cache_hits,
            consultas_rag=self.rag_queries,
            consultas_escaladas=self.escalated_queries,
            tasa_cache_hit_pct=round(cache_pct, 2),
            tasa_escalamiento_pct=round(esc_pct, 2),
            latencia_promedio_ms=round(avg_latency, 2),
            costo_estimado_usd=round(estimated_cost, 5),
            tiempo_actividad_segundos=round(uptime, 2)
        )


# Instancia singleton
metrics_service = MetricsService()
