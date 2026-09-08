"""
[DEPRECADO]: LanceDB ha sido reemplazado por Qdrant (modo local embebido)
según requerimientos del proyecto. Ver src/services/qdrant_service.py.
"""
from src.services.qdrant_service import qdrant_service as lancedb_service  # Compatibilidad retroactiva
