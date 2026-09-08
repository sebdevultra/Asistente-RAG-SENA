"""
Configuración centralizada y gestión de variables de entorno para el backend.
"""

import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables desde archivo .env local si existe
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

class Settings:
    PROJECT_NAME: str = "Asistente Virtual RAG — Academia Idiomas Colombia"
    VERSION: str = "2.0.0-opt"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    
    # LLM Cloud: Google Gemini Flash
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "AIzaSyD570QZ33pMSfy9wU0qVnNQRZxtSZEEKds")
    GEMINI_BACKUP_KEYS: list = [
        "AIzaSyD570QZ33pMSfy9wU0qVnNQRZxtSZEEKds",
        "AIzaSyAvJokYSFsxvrd10nd58yxEc7oMM7KH54E",
        "AIzaSyBrPObyLg2xlu-_N-bJnGTS3V58xygdJw0",
        "AIzaSyDU8zf7N76Y1f4Dy3Y3iWYn9MO1d5yAcos"
    ]
    GEMINI_MODEL: str = os.getenv("GEMINI_MODEL", "gemini-3.6-flash")
    GEMINI_EMBEDDING_MODEL: str = os.getenv("GEMINI_EMBEDDING_MODEL", "gemini-embedding-001")
    GEMINI_TEMPERATURE: float = float(os.getenv("GEMINI_TEMPERATURE", "0.2"))
    
    # LLM Local: Ollama (para consultas de scope alto en base vectorial >= 0.40)
    OLLAMA_ENABLED: bool = os.getenv("OLLAMA_ENABLED", "false").lower() in ("true", "1")
    OLLAMA_BASE_URL: str = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "llama3.1:8b")
    OLLAMA_TIMEOUT_SECONDS: float = float(os.getenv("OLLAMA_TIMEOUT_SECONDS", "2.5"))

    # Rutas de almacenamiento local y bases de datos
    DATA_DIR: Path = BASE_DIR / "data"
    DOCS_DIR: Path = BASE_DIR / "docs"
    QDRANT_PATH: Path = DATA_DIR / "qdrant_db"
    SQLITE_CACHE_PATH: Path = DATA_DIR / "cache_wal.db"
    
    # Servidor FastAPI
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    ADMIN_API_KEY: str = os.getenv("ADMIN_API_KEY", "admin-super-secret-key-2026")

settings = Settings()

# Garantizar que las carpetas de datos existan
settings.DATA_DIR.mkdir(parents=True, exist_ok=True)
settings.DOCS_DIR.mkdir(parents=True, exist_ok=True)
settings.QDRANT_PATH.mkdir(parents=True, exist_ok=True)
