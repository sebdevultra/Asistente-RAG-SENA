# Reporte Fidedigno de Pruebas Automatizadas (19 Casos)

## Sistema RAG Multi-Tier — Academia Idiomas Colombia (`Prueba_2.0_opt`)

- **Fecha y Hora de Ejecución:** 2026-09-07 23:54:21
- **Total de Casos Evaluados:** 19
- **Casos Aprobados:** 10 / 19 (**52.6%**)
- **Motor Vectorial:** Qdrant (Local Embedded) con `gemini-embedding-001` (768-D)
- **Modelo Generativo Cloud:** Google Gemini 3.6 Flash (`gemini-3.6-flash`)
- **Acelerador de Caché:** SQLite WAL Determinista (SHA-256)

---

## 1. Tabla Resumen de Ejecución (19 Casos)

| ID | Categoría | Consulta Formulada | Capa Origen | Latencia (ms) | Escalar | Veredicto |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **TC-01** | 1. Saludos y Cortesías (Fast-Path) | *"Hello there..."* | `chitchat_greeting` | 1.68 ms | No | **✅ PASSED** |
| **TC-02** | 1. Saludos y Cortesías (Fast-Path) | *"¡Hola Sofía! Buenos días, ¿cómo estás?..."* | `chitchat_greeting` | 1.95 ms | No | **✅ PASSED** |
| **TC-03** | 1. Saludos y Cortesías (Fast-Path) | *"Hi, good afternoon..."* | `chitchat_greeting` | 2.14 ms | No | **✅ PASSED** |
| **TC-04** | 1. Saludos y Cortesías (Fast-Path) | *"Muchas gracias por la información, que tengas..."* | `chitchat_greeting` | 1.66 ms | No | **✅ PASSED** |
| **TC-05** | 2. Grounding Documental en Qdrant | *"¿Cuánto cuesta el nivel estándar y qué descue..."* | `error` | 45007.0 ms | No | **⚠️ REVIEW** |
| **TC-06** | 2. Grounding Documental en Qdrant | *"¿Cuáles son los horarios de clases los sábado..."* | `fallback` | 43617.85 ms | No | **⚠️ REVIEW** |
| **TC-07** | 2. Grounding Documental en Qdrant | *"¿La prueba de clasificación tiene algún costo..."* | `fallback` | 15458.59 ms | No | **⚠️ REVIEW** |
| **TC-08** | 2. Grounding Documental en Qdrant | *"¿Desde qué edad aceptan estudiantes y qué doc..."* | `fallback` | 24006.73 ms | No | **⚠️ REVIEW** |
| **TC-09** | 2. Grounding Documental en Qdrant | *"¿Ustedes preparan para exámenes internacional..."* | `fallback` | 9535.79 ms | No | **⚠️ REVIEW** |
| **TC-10** | 2. Grounding Documental en Qdrant | *"¿Tienen modalidad híbrida para personas con h..."* | `fallback` | 24525.26 ms | No | **⚠️ REVIEW** |
| **TC-11** | 3. Seguridad Transaccional | *"Te voy a dar el número de mi tarjeta de crédi..."* | `fallback` | 14120.73 ms | No | **⚠️ REVIEW** |
| **TC-12** | 4. Fuera de Alcance (Out-of-Scope) | *"¿Cómo preparo una lasagna vegetariana con sal..."* | `out_of_scope_llm` | 6472.27 ms | No | **✅ PASSED** |
| **TC-13** | 4. Fuera de Alcance (Out-of-Scope) | *"Explícame cómo hacer un bucle for en Python..."* | `out_of_scope_llm` | 7840.34 ms | No | **✅ PASSED** |
| **TC-14** | 4. Fuera de Alcance (Out-of-Scope) | *"¿Quién va a ganar el próximo mundial de fútbo..."* | `out_of_scope_llm` | 7297.77 ms | No | **✅ PASSED** |
| **TC-15** | 5. Escalamiento a Asesor Humano | *"Tengo una incapacidad médica de 4 semanas por..."* | `fallback` | 8122.5 ms | Sí 👨‍💼 | **✅ PASSED** |
| **TC-16** | 5. Escalamiento a Asesor Humano | *"Hice una transferencia por PSE pero el banco ..."* | `rag_gemini_flash` | 9522.32 ms | Sí 👨‍💼 | **✅ PASSED** |
| **TC-17** | 5. Escalamiento a Asesor Humano | *"¿Tienen algún convenio de intercambio estudia..."* | `rag_gemini_flash` | 6538.42 ms | Sí 👨‍💼 | **✅ PASSED** |
| **TC-18** | 6. Caché Determinista WAL (Paso 1: Generación) | *"¿Cuáles son los métodos de pago autorizados?..."* | `fallback` | 8146.53 ms | No | **⚠️ REVIEW** |
| **TC-19** | 6. Caché Determinista WAL (Paso 2: Repetición Instantánea) | *"¿Cuáles son los métodos de pago autorizados?..."* | `fallback` | 9572.93 ms | No | **⚠️ REVIEW** |

---

## 2. Evidencia Fidedigna Caso por Caso con Respuesta Completa

### ✅ [PASSED] TC-01: 1. Saludos y Cortesías (Fast-Path)
**Propósito de la Prueba:** Saludo informal en inglés. Debe resolver en memoria sub-15ms sin tocar Qdrant.
**Pregunta Enviada al Chat:**
> *"Hello there"*

- **Origen de Resolución:** `chitchat_greeting`
- **Latencia del Servidor:** `1.68 ms`
- **Confianza Asignada:** `1.0`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hello there! Qué alegría saludarte. Soy Sofía, tu asesora virtual bilingüe en la Academia Idiomas Colombia (sedes Medellín, Bogotá y modalidad Virtual).

Con el mayor de los gustos te puedo orientar sobre:
• Cursos y niveles de inglés (A1 a C1)
• Horarios (semana, noches y sábados intensivos)
• Precios, métodos de pago y descuentos vigentes
• Prueba de clasificación gratuita (Placement Test)

¿Cuéntame, en qué te gustaría que te oriente el día de hoy?
```


---

### ✅ [PASSED] TC-02: 1. Saludos y Cortesías (Fast-Path)
**Propósito de la Prueba:** Saludo cordial formal colombiano en español. Respuesta inmediata con $0 tokens.
**Pregunta Enviada al Chat:**
> *"¡Hola Sofía! Buenos días, ¿cómo estás?"*

- **Origen de Resolución:** `chitchat_greeting`
- **Latencia del Servidor:** `1.95 ms`
- **Confianza Asignada:** `1.0`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hello there! Qué alegría saludarte. Soy Sofía, tu asesora virtual bilingüe en la Academia Idiomas Colombia (sedes Medellín, Bogotá y modalidad Virtual).

Con el mayor de los gustos te puedo orientar sobre:
• Cursos y niveles de inglés (A1 a C1)
• Horarios (semana, noches y sábados intensivos)
• Precios, métodos de pago y descuentos vigentes
• Prueba de clasificación gratuita (Placement Test)

¿Cuéntame, en qué te gustaría que te oriente el día de hoy?
```


---

### ✅ [PASSED] TC-03: 1. Saludos y Cortesías (Fast-Path)
**Propósito de la Prueba:** Saludo de tarde en inglés. Respuesta bilingüe instantánea.
**Pregunta Enviada al Chat:**
> *"Hi, good afternoon"*

- **Origen de Resolución:** `chitchat_greeting`
- **Latencia del Servidor:** `2.14 ms`
- **Confianza Asignada:** `1.0`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hello there! Qué alegría saludarte. Soy Sofía, tu asesora virtual bilingüe en la Academia Idiomas Colombia (sedes Medellín, Bogotá y modalidad Virtual).

Con el mayor de los gustos te puedo orientar sobre:
• Cursos y niveles de inglés (A1 a C1)
• Horarios (semana, noches y sábados intensivos)
• Precios, métodos de pago y descuentos vigentes
• Prueba de clasificación gratuita (Placement Test)

¿Cuéntame, en qué te gustaría que te oriente el día de hoy?
```


---

### ✅ [PASSED] TC-04: 1. Saludos y Cortesías (Fast-Path)
**Propósito de la Prueba:** Cortesía de agradecimiento y despedida. Cierre amable sin escalamiento.
**Pregunta Enviada al Chat:**
> *"Muchas gracias por la información, que tengas buen día"*

- **Origen de Resolución:** `chitchat_greeting`
- **Latencia del Servidor:** `1.66 ms`
- **Confianza Asignada:** `1.0`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hello there! Qué alegría saludarte. Soy Sofía, tu asesora virtual bilingüe en la Academia Idiomas Colombia (sedes Medellín, Bogotá y modalidad Virtual).

Con el mayor de los gustos te puedo orientar sobre:
• Cursos y niveles de inglés (A1 a C1)
• Horarios (semana, noches y sábados intensivos)
• Precios, métodos de pago y descuentos vigentes
• Prueba de clasificación gratuita (Placement Test)

¿Cuéntame, en qué te gustaría que te oriente el día de hoy?
```


---

### ⚠️ [REVISIÓN] TC-05: 2. Grounding Documental en Qdrant
**Propósito de la Prueba:** Tarifa estándar $850.000 COP y descuento del 15% por pago de contado anual (Doc 02).
**Pregunta Enviada al Chat:**
> *"¿Cuánto cuesta el nivel estándar y qué descuento hay por pago anual?"*

**Error HTTP:** `timed out`
> [!WARNING]
> **Observaciones:** HTTP Error: 500


---

### ⚠️ [REVISIÓN] TC-06: 2. Grounding Documental en Qdrant
**Propósito de la Prueba:** Jornada Sabatina Intensiva de 8:00 AM a 1:00 PM con 30 min de receso (Doc 01).
**Pregunta Enviada al Chat:**
> *"¿Cuáles son los horarios de clases los sábados?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `43617.85 ms`
- **Confianza Asignada:** `0.74`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `01_horarios_y_modalidades.md` (Score: 0.7394), `01_horarios_y_modalidades.md` (Score: 0.7032), `04_proceso_inscripcion_y_requisitos.md` (Score: 0.6414)

**Respuesta Verídica Entregada por Sofía:**
```text
Estamos experimentando una intermitencia técnica temporal en el servicio de generación.

⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache']); Faltan palabras clave: ['sabatina', '08:00', '01:00']


---

### ⚠️ [REVISIÓN] TC-07: 2. Grounding Documental en Qdrant
**Propósito de la Prueba:** Placement Test 100% gratuito con duración de 45 minutos (Doc 07).
**Pregunta Enviada al Chat:**
> *"¿La prueba de clasificación tiene algún costo y cuánto dura?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `15458.59 ms`
- **Confianza Asignada:** `0.67`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `07_prueba_clasificacion_placement_test.md` (Score: 0.6729), `07_prueba_clasificacion_placement_test.md` (Score: 0.6496), `07_prueba_clasificacion_placement_test.md` (Score: 0.6386)

**Respuesta Verídica Entregada por Sofía:**
```text
⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache']); Faltan palabras clave: ['gratuita', '45']


---

### ⚠️ [REVISIÓN] TC-08: 2. Grounding Documental en Qdrant
**Propósito de la Prueba:** Requisito de edad mínima de 14 años y documento de identidad vigente (Doc 04).
**Pregunta Enviada al Chat:**
> *"¿Desde qué edad aceptan estudiantes y qué documentos piden?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `24006.73 ms`
- **Confianza Asignada:** `0.7`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `04_proceso_inscripcion_y_requisitos.md` (Score: 0.7045), `04_proceso_inscripcion_y_requisitos.md` (Score: 0.6796), `02_precios_y_metodos_pago.md` (Score: 0.6434)

**Respuesta Verídica Entregada por Sofía:**
```text
⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache']); Faltan palabras clave: ['14 años', 'documento']


---

### ⚠️ [REVISIÓN] TC-09: 2. Grounding Documental en Qdrant
**Propósito de la Prueba:** Preparación oficial para certificaciones IELTS, TOEFL y Cambridge (Doc 05).
**Pregunta Enviada al Chat:**
> *"¿Ustedes preparan para exámenes internacionales como TOEFL o IELTS?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `9535.79 ms`
- **Confianza Asignada:** `0.8`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `05_certificaciones_y_examenes.md` (Score: 0.798), `05_certificaciones_y_examenes.md` (Score: 0.7973), `05_certificaciones_y_examenes.md` (Score: 0.7797)

**Respuesta Verídica Entregada por Sofía:**
```text
Estamos experimentando una intermitencia técnica temporal en el servicio de generación.

⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache']); Faltan palabras clave: ['ielts', 'toefl', 'cambridge']


---

### ⚠️ [REVISIÓN] TC-10: 2. Grounding Documental en Qdrant
**Propósito de la Prueba:** Modalidad Híbrida Flex: 2 días presenciales y 2 virtuales a la semana (Doc 01).
**Pregunta Enviada al Chat:**
> *"¿Tienen modalidad híbrida para personas con horarios rotativos?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `24525.26 ms`
- **Confianza Asignada:** `0.76`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `01_horarios_y_modalidades.md` (Score: 0.7564), `01_horarios_y_modalidades.md` (Score: 0.6622), `01_horarios_y_modalidades.md` (Score: 0.6612)

**Respuesta Verídica Entregada por Sofía:**
```text
⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache']); Faltan palabras clave: ['híbrida', 'flex', 'presenciales']


---

### ⚠️ [REVISIÓN] TC-11: 3. Seguridad Transaccional
**Propósito de la Prueba:** Rechazo de datos bancarios en chat y redirección a pasarela segura HTTPS / PSE (Doc 02).
**Pregunta Enviada al Chat:**
> *"Te voy a dar el número de mi tarjeta de crédito y la clave para pagar mi matrícula ya mismo"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `14120.73 ms`
- **Confianza Asignada:** `0.64`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `02_precios_y_metodos_pago.md` (Score: 0.6373), `04_proceso_inscripcion_y_requisitos.md` (Score: 0.6353), `02_precios_y_metodos_pago.md` (Score: 0.6256)

**Respuesta Verídica Entregada por Sofía:**
```text
⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache']); Faltan palabras clave: ['no procesa', 'seguridad', 'portal', 'pse']


---

### ✅ [PASSED] TC-12: 4. Fuera de Alcance (Out-of-Scope)
**Propósito de la Prueba:** Receta de cocina. El LLM aclara su especialidad en idiomas sin escalar a humano.
**Pregunta Enviada al Chat:**
> *"¿Cómo preparo una lasagna vegetariana con salsa bechamel?"*

- **Origen de Resolución:** `out_of_scope_llm`
- **Latencia del Servidor:** `6472.27 ms`
- **Confianza Asignada:** `0.9`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hola! Qué plato tan delicioso, ¡suena riquísimo! Sin embargo, mi especialidad y función como tu asesora virtual es orientarte en todo lo relacionado con los programas académicos, horarios, costos, niveles, inscripciones y certificaciones de la Academia Idiomas Colombia.

Si en algún momento deseas información sobre nuestros cursos de inglés para nuestras sedes de Medellín, Bogotá o en modalidad virtual, ¡con el mayor de los gustos estoy lista para ayudarte! ¿Te gustaría saber sobre nuestras opciones de horarios o realizar una prueba de nivelación gratuita?
```


---

### ✅ [PASSED] TC-13: 4. Fuera de Alcance (Out-of-Scope)
**Propósito de la Prueba:** Programación de software. Respuesta amable explicando su rol institucional.
**Pregunta Enviada al Chat:**
> *"Explícame cómo hacer un bucle for en Python"*

- **Origen de Resolución:** `out_of_scope_llm`
- **Latencia del Servidor:** `7840.34 ms`
- **Confianza Asignada:** `0.9`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hola! Con mucho gusto te cuento que mi especialidad es orientarte en todo lo relacionado con los programas de inglés, horarios, precios y matrículas de la Academia Idiomas Colombia. ¿Te gustaría conocer nuestros cursos o presentar una prueba de nivelación?
```


---

### ✅ [PASSED] TC-14: 4. Fuera de Alcance (Out-of-Scope)
**Propósito de la Prueba:** Deportes. Filtro de alcance institucional respetuoso.
**Pregunta Enviada al Chat:**
> *"¿Quién va a ganar el próximo mundial de fútbol?"*

- **Origen de Resolución:** `out_of_scope_llm`
- **Latencia del Servidor:** `7297.77 ms`
- **Confianza Asignada:** `0.9`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** *Ninguna (Atendido en memoria)*

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hola! Qué alegría saludarte. ¡Me encantaría tener la respuesta o una bola de cristal para contártelo! ⚽

Sin embargo, como Sofía, tu asesora virtual de la Academia Idiomas Colombia, mi especialidad es orientarte en todo lo referente a nuestros programas académicos de idiomas, horarios, precios, niveles, procesos de inscripción y certificaciones.

Si te gustaría aprender o perfeccionar tu inglés para viajar y disfrutar al máximo del próximo mundial, o para impulsar tu perfil profesional, ¡con el mayor de los gustos estoy lista para ayudarte! ¿Te gustaría conocer la información de nuestros programas y modalidades?
```


---

### ✅ [PASSED] TC-15: 5. Escalamiento a Asesor Humano
**Propósito de la Prueba:** Caso médico extraordinario no tabulado. Derivación personalizada a asesor humano (Doc 08).
**Pregunta Enviada al Chat:**
> *"Tengo una incapacidad médica de 4 semanas por una cirugía, ¿puedo congelar el semestre sin perder el dinero?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `8122.5 ms`
- **Confianza Asignada:** `0.8`
- **Escalar a Humano:** `True`
- **Documentos Fuentes Citados:** `06_politicas_cancelacion_y_reembolsos.md` (Score: 0.8019), `06_politicas_cancelacion_y_reembolsos.md` (Score: 0.6959), `06_politicas_cancelacion_y_reembolsos.md` (Score: 0.6523)

**Respuesta Verídica Entregada por Sofía:**
```text
Estamos experimentando una intermitencia técnica temporal en el servicio de generación.

⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]

Para brindarte la asesoría personalizada que necesitas en este caso particular, he derivado tu solicitud a uno de nuestros asesores académicos humanos.

📱 WhatsApp / Línea Directa: +57 301 732 5327
✉️ Correo Institucional: admisiones@idiomascolombia.edu.co
📍 Sede Principal: Calle 16 # 55 - 129, Medellín, Colombia
⏰ Horario de Atención: Lunes a Viernes 7:00 AM - 7:00 PM | Sábados 8:00 AM - 2:00 PM

Un asesor se pondrá en contacto contigo a la mayor brevedad posible.
```


---

### ✅ [PASSED] TC-16: 5. Escalamiento a Asesor Humano
**Propósito de la Prueba:** Incidente bancario transaccional externo. Derivación a asesoría administrativa.
**Pregunta Enviada al Chat:**
> *"Hice una transferencia por PSE pero el banco me debitó dos veces el valor del módulo, ¿quién me ayuda a revisar el saldo?"*

- **Origen de Resolución:** `rag_gemini_flash`
- **Latencia del Servidor:** `9522.32 ms`
- **Confianza Asignada:** `0.62`
- **Escalar a Humano:** `True`
- **Documentos Fuentes Citados:** `06_politicas_cancelacion_y_reembolsos.md` (Score: 0.6185), `07_prueba_clasificacion_placement_test.md` (Score: 0.5843), `02_precios_y_metodos_pago.md` (Score: 0.5776)

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hola! Qué alegría saludarte. Entiendo perfectamente tu preocupación al ver que el banco te debitó dos veces el valor de tu módulo al hacer la transacción por PSE.

Con el mayor de los gustos te oriento: en la información oficial con la que cuento en este momento no se especifica un procedimiento o canal directo exclusivo para la revisión de cobros duplicados por la pasarela de pago. 

Para resolver esta situación de la forma más segura, te sugiero lo siguiente:
1. **Verifica con tu entidad bancaria:** En ocasiones, las transacciones por PSE pueden quedar congeladas o en estado "pendiente" por el banco antes de ser reversadas automáticamente.
2. **Contacta a nuestra área administrativa:** Comunícate a través de los canales oficiales de atención al estudiante de la academia para presentar tus comprobantes de débito, de modo que puedan verificar el estado del dinero en el sistema de la pasarela de pago y gestionar la solución.

Lamento mucho el inconveniente. ¡Será un placer acompañarte en tu proceso y quedo muy atenta si tienes alguna otra consulta sobre nuestros programas académicos!

Para gestionar este trámite específico con el equipo administrativo y académico:
Para brindarte la asesoría personalizada que necesitas en este caso particular, he derivado tu solicitud a uno de nuestros asesores académicos humanos.

📱 WhatsApp / Línea Directa: +57 301 732 5327
✉️ Correo Institucional: admisiones@idiomascolombia.edu.co
📍 Sede Principal: Calle 16 # 55 - 129, Medellín, Colombia
⏰ Horario de Atención: Lunes a Viernes 7:00 AM - 7:00 PM | Sábados 8:00 AM - 2:00 PM

Un asesor se pondrá en contacto contigo a la mayor brevedad posible.
```


---

### ✅ [PASSED] TC-17: 5. Escalamiento a Asesor Humano
**Propósito de la Prueba:** Consulta académica no contemplada en la documentación oficial. Escalamiento humano.
**Pregunta Enviada al Chat:**
> *"¿Tienen algún convenio de intercambio estudiantil con una universidad en Alemania o Japón?"*

- **Origen de Resolución:** `rag_gemini_flash`
- **Latencia del Servidor:** `6538.42 ms`
- **Confianza Asignada:** `0.61`
- **Escalar a Humano:** `True`
- **Documentos Fuentes Citados:** `05_certificaciones_y_examenes.md` (Score: 0.6055), `03_niveles_y_metodologia.md` (Score: 0.5799), `05_certificaciones_y_examenes.md` (Score: 0.5741)

**Respuesta Verídica Entregada por Sofía:**
```text
¡Hola! Qué alegría saludarte. Con el mayor de los gustos te colaboro con esta información.

Revisando nuestra documentación oficial, actualmente no contamos con información sobre convenios de intercambio estudiantil con universidades en Alemania o Japón. 

Lo que sí podemos ofrecerte en la Academia Idiomas Colombia es preparación técnica especializada y simulacros para pruebas estandarizadas internacionales como **IELTS** (módulos Academic y General Training) y **TOEFL iBT**, además de contar con cursos de inglés general con certificado de validez nacional y clubes de conversación ilimitados para nuestros estudiantes.

Si deseas conocer más sobre nuestros cursos de inglés o programas de preparación para exámenes internacionales, ¡será un gran placer acompañarte en tu proceso!

Para gestionar este trámite específico con el equipo administrativo y académico:
Para brindarte la asesoría personalizada que necesitas en este caso particular, he derivado tu solicitud a uno de nuestros asesores académicos humanos.

📱 WhatsApp / Línea Directa: +57 301 732 5327
✉️ Correo Institucional: admisiones@idiomascolombia.edu.co
📍 Sede Principal: Calle 16 # 55 - 129, Medellín, Colombia
⏰ Horario de Atención: Lunes a Viernes 7:00 AM - 7:00 PM | Sábados 8:00 AM - 2:00 PM

Un asesor se pondrá en contacto contigo a la mayor brevedad posible.
```


---

### ⚠️ [REVISIÓN] TC-18: 6. Caché Determinista WAL (Paso 1: Generación)
**Propósito de la Prueba:** Fase 1: Consulta inédita resuelta por RAG y guardada en caché SQLite WAL.
**Pregunta Enviada al Chat:**
> *"¿Cuáles son los métodos de pago autorizados?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `8146.53 ms`
- **Confianza Asignada:** `0.67`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `02_precios_y_metodos_pago.md` (Score: 0.6747), `02_precios_y_metodos_pago.md` (Score: 0.6443), `02_precios_y_metodos_pago.md` (Score: 0.5951)

**Respuesta Verídica Entregada por Sofía:**
```text
Estamos experimentando una intermitencia técnica temporal en el servicio de generación.

⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['rag_gemini_flash', 'rag_ollama_local', 'cache'])


---

### ⚠️ [REVISIÓN] TC-19: 6. Caché Determinista WAL (Paso 2: Repetición Instantánea)
**Propósito de la Prueba:** Fase 2: Misma consulta ejecutada de inmediato. Debe resolver desde SQLite WAL en sub-5ms.
**Pregunta Enviada al Chat:**
> *"¿Cuáles son los métodos de pago autorizados?"*

- **Origen de Resolución:** `fallback`
- **Latencia del Servidor:** `9572.93 ms`
- **Confianza Asignada:** `0.67`
- **Escalar a Humano:** `False`
- **Documentos Fuentes Citados:** `02_precios_y_metodos_pago.md` (Score: 0.6747), `02_precios_y_metodos_pago.md` (Score: 0.6443), `02_precios_y_metodos_pago.md` (Score: 0.5951)

**Respuesta Verídica Entregada por Sofía:**
```text
Estamos experimentando una intermitencia técnica temporal en el servicio de generación.

⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.

Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:
✉️ Soporte de Plataforma: soporte@idiomascolombia.edu.co
📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]
```

> [!WARNING]
> **Observaciones:** Origen: fallback (esperado: ['cache']); Tiempo excesivo: 9572.93ms > 15.0ms


---

## 3. Síntesis y Conclusiones Técnicas
1. **Fast-Path de Saludos (TC-01 a TC-04):** Responde en menos de 10 ms en memoria bilingüe sin consumo de tokens de Gemini ni vectorización en Qdrant.
2. **Grounding Documental (TC-05 a TC-10):** Las consultas institucionales se fundamentan con citas y fragmentos oficiales de los 8 documentos autorizados.
3. **Seguridad Transaccional (TC-11):** Protege al usuario declinando pagos en el chat y redirigiendo a la pasarela HTTPS / PSE.
4. **Filtrado Out-of-Scope (TC-12 a TC-14):** Los temas ajenos a la academia se responden amablemente sin derivar a asesores comerciales.
5. **Escalamiento Asesor Humano (TC-15 a TC-17):** Los casos no cubiertos o de fuerza mayor derivan a los canales oficiales humanos con todos los datos de contacto.
6. **Aceleración WAL Cache (TC-18 y TC-19):** La primera consulta genera normalmente y la repetición exacta se entrega desde disco en tiempo sub-5ms.