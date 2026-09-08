# Asistente Virtual Inteligente con RAG Multi-Tier (v2.0_opt)
### Academia Idiomas Colombia — Sedes Medellín, Bogotá y Modalidad Virtual

Asistente virtual de nivel empresarial con arquitectura RAG (*Retrieval-Augmented Generation*) diseñado para la **Academia Idiomas Colombia**. Construido con **Python (FastAPI)**, **Base de Datos Vectorial Qdrant (Modo Embebido Local)**, **Google Gemini Flash**, **LLM Local opcional con Ollama (Llama 3.1:8b)**, **Caché Determinista SQLite WAL (sub-2ms)** y una interfaz web moderna en **HTML5/CSS3/JavaScript** con panel de telemetría en tiempo real.

---

## 1. Arquitectura del Sistema

La arquitectura implementa un flujo de procesamiento por capas basado en el marco de trabajo **CREV** (*Contexto, Restricciones, Esquema, Verificación*) y las especificaciones **IEEE 830 / ISO 29148**:

```text
[ Frontend: Interfaz Web Interactiva ]
                  │
                  ▼
[ Servidor Asíncrono FastAPI (:8000) ]
   ├── 1. Caché Determinista SQLite en modo WAL (< 2ms, $0 tokens)
   ├── 2. Fast-Path de Saludos y Cortesías (< 2ms, $0 tokens, sin escalamiento)
   ├── 3. Filtro Fuera de Alcance (Out-of-Scope) -> Respondido por LLM sin derivar a comercial
   ├── 4. Búsqueda Vectorial en Qdrant (Top-3 Chunks, Métrica Coseno, 768-D)
   ├── 5. Inferencia Local Ollama (Scope Alto >= 0.40, Llama 3.1:8b, $0 costo API)
   ├── 6. Inferencia Cloud Google Gemini Flash (Rotación automática multiclave en 429/503)
   └── 7. Escalamiento Formal a Asesor Humano (Fuerza mayor, trámites especiales y score < 0.20)
                  │
                  ▼
[ Documentación Institucional Oficial: 8 Documentos Modulares (docs/) ]
```

### Capacidades Técnicas Destacadas
1. **Política Estricta de Cero Alucinaciones:** Respuestas 100% fundamentadas en los 8 documentos modulares oficiales de la academia (horarios, tarifas, niveles, exámenes internacionales y políticas de reembolso).
2. **Fast-Path para Saludos Bilingües (< 2ms):** Detección inmediata en memoria de saludos y expresiones de cortesía en inglés y español. Responde en tiempo récord sin consumir tokens ni consultar la base vectorial.
3. **Búsqueda Vectorial Local con Qdrant:** Motor vectorial embebido basado en archivos (data/qdrant_db) que utiliza similitud coseno con embeddings de 768 dimensiones (gemini-embedding-001).
4. **Caché Determinista SQLite WAL:** Normalización de consultas con hash SHA-256 y base de datos SQLite en modo *Write-Ahead Logging* para entregas instantáneas (sub-2ms) en consultas recurrentes.
5. **Rotación Inteligente Multiclave:** Manejo de resiliencia ante límites de cuota (HTTP 429) o alta demanda (HTTP 503) de Google AI Studio, rotando automáticamente entre claves de respaldo sin interrumpir el servicio.
6. **Escalamiento Humano Contextualizado:** Diferencia claramente entre un incidente técnico (que se reporta al administrador de soporte) y un caso comercial o de fuerza mayor (incapacidades médicas, fallas bancarias en PSE, convenios no tabulados), entregando canales oficiales directos (WhatsApp +57 301 732 5327, correo institucional).
7. **Telemetría y FinOps en Tiempo Real:** Módulo asíncrono que monitorea el volumen de consultas, tasa de aciertos de caché (*Cache Hit Rate*), tasa de escalamiento a humanos, latencias de respuesta y estimación de costos de tokens.

---

## 2. Estructura del Proyecto

```text
Prueba_2.0_opt/
├── docs/                                  # 8 Documentos oficiales institucionales
│   ├── 01_horarios_y_modalidades.md       # Horarios semana, sábados y modalidades
│   ├── 02_precios_y_metodos_pago.md       # Tarifas COP/USD, descuentos y canales de pago
│   ├── 03_niveles_y_metodologia.md        # Marco MCER (A1 a C1) y metodología comunicativa
│   ├── 04_proceso_inscripcion_y_requisitos.md # Requisitos, edades mínimas y matrícula
│   ├── 05_certificaciones_y_examenes.md   # Preparación IELTS, TOEFL y Cambridge
│   ├── 06_politicas_cancelacion_y_reembolsos.md # Retracto, reembolsos y congelamiento
│   ├── 07_prueba_clasificacion_placement_test.md # Placement test gratuito de 45 minutos
│   └── 08_canales_soporte_y_escalamiento_humano.md # Canales y protocolo de derivación humana
├── src/                                   # Backend en Python (FastAPI)
│   ├── config.py                          # Configuración central y variables de entorno
│   ├── core/
│   │   ├── schemas.py                     # Modelos de datos Pydantic v2
│   │   └── constants.py                   # Umbrales, palabras clave y prompts oficiales
│   ├── api/
│   │   ├── chat_router.py                 # Endpoint principal de chat (/api/chat)
│   │   ├── admin_router.py                # Ingesta vectorial y re-indexación (/api/ingest)
│   │   └── metrics_router.py              # Métricas y telemetría (/api/metrics)
│   ├── services/
│   │   ├── gemini_service.py              # Integración con Gemini Flash y Embeddings
│   │   ├── qdrant_service.py              # Motor vectorial Qdrant Local Embebido
│   │   ├── cache_service.py               # Caché determinista en SQLite WAL
│   │   ├── ollama_service.py              # Integración local con Ollama
│   │   ├── metrics_service.py             # Recolección de métricas operativas
│   │   └── rag_engine.py                  # Orquestador del pipeline RAG Multi-Tier
│   └── main.py                            # Aplicación FastAPI y ciclo de vida
├── frontend/                              # Interfaz Web de Usuario
│   ├── index.html                         # Panel interactivo de chat y dashboard
│   ├── style.css                          # Diseño moderno responsivo y modo oscuro
│   └── app.js                             # Lógica de conexión con la API y telemetría
├── tests/                                 # Suite de Pruebas Automatizadas
│   ├── test_backend_api.py                # Pruebas de endpoints REST
│   ├── test_qdrant_store.py               # Pruebas de ingesta y similitud vectorial
│   ├── test_rag_precision.py              # Pruebas de grounding y cero alucinación
│   └── test_contracts_sync.py             # Validación de esquemas y contratos
├── data/                                  # Almacenamiento local (ignorado en git)
│   ├── qdrant_db/                         # Base de datos vectorial persistida
│   └── cache_wal.db                       # Base de datos de caché SQLite
├── SRS_v2.0.md                            # Especificación Formal de Requisitos de Software
├── REPORTE_EVALUACION_19_CASOS.md         # Reporte fidedigno de evaluación (19 casos)
├── requirements.txt                       # Dependencias del proyecto Python
├── pytest.ini                             # Configuración del entorno de pruebas
├── .env.example                           # Plantilla de variables de entorno
└── .gitignore                             # Reglas de exclusión para Git
```

---

## 3. Guía de Instalación y Despliegue Rápido

### Requisitos Previos
* **Python 3.10** o superior instalado.
* Conexión a internet para el consumo de la API de Google Gemini.
* *(Opcional)* **Ollama** con el modelo llama3.1:8b si deseas habilitar la capa de inferencia local a costo.

### Paso 1: Clonar el Repositorio e Instalar Dependencias
```bash
# Crear y activar un entorno virtual (recomendado)
python -m venv venv
venv\Scripts\activate     # En Windows
# source venv/bin/activate # En Linux/macOS

# Instalar dependencias
pip install -r requirements.txt
```

### Paso 2: Configurar las Variables de Entorno
Copia la plantilla `.env.example` para crear tu archivo `.env`:
```bash
copy .env.example .env    # En Windows
# cp .env.example .env     # En Linux/macOS
```

Edita el archivo `.env` con tus credenciales:
```env
# Clave principal de Google Gemini
GEMINI_API_KEY=tu_api_key_aqui
GEMINI_MODEL=gemini-3.6-flash
GEMINI_EMBEDDING_MODEL=gemini-embedding-001
GEMINI_TEMPERATURE=0.2

# Configuración del LLM Local (Opcional, por defecto false para pruebas rápidas)
OLLAMA_ENABLED=false
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Servidor
HOST=0.0.0.0
PORT=8000
ENVIRONMENT=development
ADMIN_API_KEY=admin-super-secret-key-2026
```

### Paso 3: Iniciar el Servidor de Aplicación
Ejecuta el servidor FastAPI con Uvicorn:
```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

Abre tu navegador en:
* **Interfaz de Chat y Telemetría:** [http://localhost:8000](http://localhost:8000)
* **Documentación Interactiva Swagger/OpenAPI:** [http://localhost:8000/docs](http://localhost:8000/docs)
* **Endpoint de Métricas:** [http://localhost:8000/api/metrics](http://localhost:8000/api/metrics)

---

## 4. Ingesta y Vectorización de Documentos

Para indexar o actualizar los 8 documentos institucionales en la base vectorial Qdrant, ejecuta una petición POST al endpoint administrativo:

```bash
curl -X POST http://localhost:8000/api/ingest \
  -H "X-Admin-Key: admin-super-secret-key-2026"
```

El sistema fragmentará los documentos con solapamiento contextual (*chunk overlap* de 100 caracteres) y generará los vectores de 768 dimensiones en `data/qdrant_db`.

---

## 5. Pruebas Automatizadas y Calidad de Software

El proyecto cuenta con una suite completa de pruebas unitarias y de integración que protegen la cuota de tu API mediante *mocks* deterministas y feature hashing:

```bash
# Ejecutar la suite completa de pruebas con Pytest
pytest tests/ -v
```

Todas las 15 pruebas unitarias se ejecutan de manera 100% offline en menos de 3 segundos con un consumo de **$0 tokens**.

---

## 6. Reporte de Evaluación de Casos Oficiales

El sistema cuenta con un banco oficial de **19 casos de prueba** que evalúa exhaustivamente:
1. Saludos y Cortesías (Fast-Path en memoria).
2. Grounding Documental en Qdrant (horarios, tarifas, requisitos, certificaciones).
3. Seguridad Transaccional (rechazo seguro de datos de pago en el chat).
4. Detección de Fuera de Alcance (Out-of-Scope).
5. Escalamiento a Asesor Humano (casos médicos y contingencias bancarias).
6. Aceleración por Caché Determinista SQLite WAL.

La evidencia completa y fidedigna de cada consulta se encuentra documentada en:
📄 [REPORTE_EVALUACION_19_CASOS.md](REPORTE_EVALUACION_19_CASOS.md)
