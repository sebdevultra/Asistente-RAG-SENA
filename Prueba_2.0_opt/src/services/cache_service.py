"""
Servicio de Caché Determinista con SQLite en modo WAL (Write-Ahead Logging).
Proporciona recuperación de respuestas en tiempo sub-2ms para consultas frecuentes.
"""

import asyncio
import hashlib
import json
import logging
import re
import sqlite3
from typing import Optional, Dict, Any
from src.config import settings

logger = logging.getLogger("cache_service")

class CacheService:
    def __init__(self):
        self.db_path = str(settings.SQLITE_CACHE_PATH)
        self._init_db()

    def _init_db(self):
        """
        Inicializa SQLite con WAL mode para máxima concurrencia y lecturas rápidas.
        """
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("PRAGMA journal_mode=WAL;")
                cursor.execute("PRAGMA synchronous=NORMAL;")
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS response_cache (
                        query_hash TEXT PRIMARY KEY,
                        normalized_query TEXT NOT NULL,
                        response_json TEXT NOT NULL,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        hit_count INTEGER DEFAULT 1
                    );
                """)
                cursor.execute("CREATE INDEX IF NOT EXISTS idx_query_hash ON response_cache(query_hash);")
                conn.commit()
            logger.info("SQLite WAL Cache inicializado correctamente.")
        except Exception as e:
            logger.error(f"Error inicializando SQLite WAL Cache: {e}")

    @staticmethod
    def normalize_query(query: str) -> str:
        """
        Normaliza el texto para maximizar la tasa de acierto de caché.
        Convierte a minúsculas, elimina puntuación redundante y colapsa espacios.
        """
        text = query.lower().strip()
        text = re.sub(r"[^\w\s\?¿áéíóúüñ]", "", text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    def _hash_query(self, normalized_query: str) -> str:
        return hashlib.sha256(normalized_query.encode("utf-8")).hexdigest()

    async def get(self, query: str) -> Optional[Dict[str, Any]]:
        """
        Busca una consulta en la caché. Retorna el payload deserializado si existe.
        """
        normalized = self.normalize_query(query)
        q_hash = self._hash_query(normalized)

        def _sync_get():
            try:
                with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute(
                        "SELECT response_json FROM response_cache WHERE query_hash = ?",
                        (q_hash,)
                    )
                    row = cursor.fetchone()
                    if row:
                        # Incrementar contador de hits
                        cursor.execute(
                            "UPDATE response_cache SET hit_count = hit_count + 1 WHERE query_hash = ?",
                            (q_hash,)
                        )
                        conn.commit()
                        return json.loads(row[0])
            except Exception as e:
                logger.error(f"Error leyendo de caché: {e}")
            return None

        return await asyncio.to_thread(_sync_get)

    async def set(self, query: str, response_payload: Dict[str, Any]):
        """
        Almacena una respuesta en la caché SQLite de forma no bloqueante.
        """
        normalized = self.normalize_query(query)
        q_hash = self._hash_query(normalized)
        data_json = json.dumps(response_payload, ensure_ascii=False)

        def _sync_set():
            try:
                with sqlite3.connect(self.db_path, timeout=5.0) as conn:
                    cursor = conn.cursor()
                    cursor.execute("""
                        INSERT INTO response_cache (query_hash, normalized_query, response_json)
                        VALUES (?, ?, ?)
                        ON CONFLICT(query_hash) DO UPDATE SET
                            response_json = excluded.response_json,
                            hit_count = hit_count + 1;
                    """, (q_hash, normalized, data_json))
                    conn.commit()
            except Exception as e:
                logger.error(f"Error guardando en caché: {e}")

        await asyncio.to_thread(_sync_set)

    async def clear(self):
        """Limpia todos los registros de la caché."""
        def _sync_clear():
            with sqlite3.connect(self.db_path) as conn:
                conn.execute("DELETE FROM response_cache;")
                conn.commit()
        await asyncio.to_thread(_sync_clear)


# Instancia singleton
cache_service = CacheService()
