"""
Servicio de Base de Datos Vectorial Qdrant (Modo Local Embebido).
Indexa y recupera fragmentos documentales mediante similitud de Coseno.
"""

import asyncio
import logging
import math
import uuid
from pathlib import Path
from typing import List, Dict, Any, Optional
from src.config import settings
from src.core.constants import CHUNK_SIZE_CHARS, CHUNK_OVERLAP_CHARS, MAX_TOP_K_CHUNKS
from src.services.gemini_service import gemini_service

logger = logging.getLogger("qdrant_service")

COLLECTION_NAME = "knowledge_chunks"
VECTOR_DIM = 768

class QdrantService:
    def __init__(self):
        self.db_path = str(settings.QDRANT_PATH)
        self._client = None
        self._is_qdrant_available = False
        self._in_memory_fallback: List[Dict[str, Any]] = []
        self._init_db()

    def _init_db(self):
        try:
            from qdrant_client import QdrantClient
            from qdrant_client.models import Distance, VectorParams

            self._client = QdrantClient(path=self.db_path)
            self._is_qdrant_available = True

            collections = [c.name for c in self._client.get_collections().collections]
            if COLLECTION_NAME not in collections:
                self._client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=VECTOR_DIM, distance=Distance.COSINE)
                )
                logger.info(f"Colección Qdrant '{COLLECTION_NAME}' creada exitosamente.")
            else:
                logger.info(f"Colección Qdrant '{COLLECTION_NAME}' conectada y lista.")
        except Exception as e:
            logger.warning(f"Qdrant nativo no disponible ({e}). Operando con motor vectorial embebido.")
            self._is_qdrant_available = False

    def is_ready(self) -> bool:
        if self._is_qdrant_available and self._client is not None:
            try:
                info = self._client.get_collection(COLLECTION_NAME)
                return info.points_count > 0
            except Exception:
                return False
        return len(self._in_memory_fallback) > 0

    def _chunk_text(self, text: str, doc_name: str) -> List[Dict[str, Any]]:
        chunks = []
        start = 0
        text_len = len(text)
        chunk_idx = 0

        while start < text_len:
            end = min(start + CHUNK_SIZE_CHARS, text_len)
            chunk_content = text[start:end].strip()
            if chunk_content:
                chunks.append({
                    "id": f"{doc_name}_{chunk_idx}",
                    "doc_name": doc_name,
                    "text": chunk_content,
                    "chunk_index": chunk_idx
                })
                chunk_idx += 1
            if end >= text_len:
                break
            start += (CHUNK_SIZE_CHARS - CHUNK_OVERLAP_CHARS)

        return chunks

    async def ingest_documents(self, docs_dir: Optional[Path] = None) -> Dict[str, Any]:
        """
        Lee los 8 documentos de negocio en docs/, calcula embeddings y los indexa en Qdrant.
        """
        target_dir = docs_dir or settings.DOCS_DIR
        doc_files = sorted(list(target_dir.glob("*.md")))
        
        if not doc_files:
            raise FileNotFoundError(f"No se encontraron archivos .md en {target_dir}")

        all_raw_chunks = []
        for doc_file in doc_files:
            content = doc_file.read_text(encoding="utf-8")
            raw_chunks = self._chunk_text(content, doc_file.name)
            all_raw_chunks.extend(raw_chunks)

        logger.info(f"Generando embeddings para {len(all_raw_chunks)} chunks con Gemini...")
        
        records = []
        for chunk in all_raw_chunks:
            vector = await gemini_service.generate_embedding(chunk["text"])
            records.append({
                "id": chunk["id"],
                "doc_name": chunk["doc_name"],
                "text": chunk["text"],
                "chunk_index": chunk["chunk_index"],
                "vector": vector
            })

        # Almacenar en Qdrant
        if self._is_qdrant_available and self._client is not None:
            from qdrant_client.models import PointStruct, Distance, VectorParams

            def _sync_write():
                if self._client.collection_exists(COLLECTION_NAME):
                    self._client.delete_collection(COLLECTION_NAME)
                self._client.create_collection(
                    collection_name=COLLECTION_NAME,
                    vectors_config=VectorParams(size=len(records[0]["vector"]), distance=Distance.COSINE)
                )
                points = []
                for idx, r in enumerate(records):
                    points.append(
                        PointStruct(
                            id=idx,
                            vector=r["vector"],
                            payload={
                                "chunk_id": r["id"],
                                "doc_name": r["doc_name"],
                                "text": r["text"],
                                "chunk_index": r["chunk_index"]
                            }
                        )
                    )
                self._client.upsert(collection_name=COLLECTION_NAME, points=points)
                logger.info(f"{len(points)} puntos insertados en Qdrant exitosamente.")

            await asyncio.to_thread(_sync_write)
        else:
            self._in_memory_fallback = records

        logger.info(f"Ingestión completada: {len(doc_files)} docs, {len(records)} chunks indexados.")
        return {
            "documentos_procesados": len(doc_files),
            "total_chunks": len(records),
            "status": "success"
        }

    async def search(
        self,
        query: str,
        top_k: int = MAX_TOP_K_CHUNKS
    ) -> List[Dict[str, Any]]:
        """
        Búsqueda vectorial semántica en Qdrant con métrica de Coseno normalizada.
        """
        query_vector = await gemini_service.generate_embedding(query)

        if self._is_qdrant_available and self._client is not None:
            def _sync_search():
                try:
                    if hasattr(self._client, "query_points"):
                        res = self._client.query_points(
                            collection_name=COLLECTION_NAME,
                            query=query_vector,
                            limit=top_k,
                            with_payload=True
                        )
                        return res.points if hasattr(res, "points") else res
                    elif hasattr(self._client, "search"):
                        return self._client.search(
                            collection_name=COLLECTION_NAME,
                            query_vector=query_vector,
                            limit=top_k
                        )
                except Exception as ex:
                    logger.error(f"Error en búsqueda Qdrant: {ex}")
                return []

            hits = await asyncio.to_thread(_sync_search)
            normalized = []
            for hit in hits:
                payload = hit.payload or {}
                # Qdrant cosine similarity está en [-1, 1], normalizado a [0, 1]
                score = max(0.0, min(1.0, float(hit.score)))
                normalized.append({
                    "doc_name": payload.get("doc_name", "documento_oficial.md"),
                    "text": payload.get("text", ""),
                    "score": round(score, 4)
                })
            return normalized

        # Fallback de memoria
        return self._in_memory_search(query_vector, top_k)

    def _in_memory_search(self, query_vector: List[float], top_k: int) -> List[Dict[str, Any]]:
        scored = []
        for item in self._in_memory_fallback:
            vec = item.get("vector", [])
            dot = sum(a * b for a, b in zip(query_vector, vec))
            norm_a = math.sqrt(sum(a * a for a in query_vector)) or 1.0
            norm_b = math.sqrt(sum(b * b for b in vec)) or 1.0
            sim = max(0.0, min(1.0, dot / (norm_a * norm_b)))
            scored.append((sim, item))

        scored.sort(key=lambda x: x[0], reverse=True)
        top = scored[:top_k]
        return [
            {
                "doc_name": it[1].get("doc_name", "desconocido.md"),
                "text": it[1].get("text", ""),
                "score": round(it[0], 4)
            }
            for it in top
        ]


# Instancia singleton
qdrant_service = QdrantService()
