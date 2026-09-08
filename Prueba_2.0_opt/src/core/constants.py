"""
Constantes operativas, umbrales y prompts institucionales para el Asistente RAG.
"""

# Umbrales de decisión RAG y Enrutamiento Multi-Tier
SIMILARITY_LOCAL_LLM_THRESHOLD = 0.40  # >= 0.40: Inferencia local con Ollama ($0 tokens, alta similitud semántica)
SIMILARITY_ESCALATION_THRESHOLD = 0.20 # < 0.20: Escalamiento a asesor humano (contexto de academia pero sin soporte)
MAX_TOP_K_CHUNKS = 3                   # Número de fragmentos a recuperar en Qdrant
CHUNK_SIZE_CHARS = 600                 # Tamaño del chunk de texto
CHUNK_OVERLAP_CHARS = 100              # Solapamiento entre chunks para conservar contexto

# Canales de soporte oficial para derivación humana
ACADEMY_PHONE = "+57 301 732 5327"
ACADEMY_EMAIL_ADMISSIONS = "admisiones@idiomascolombia.edu.co"
ACADEMY_EMAIL_SUPPORT = "soporte@idiomascolombia.edu.co"
ACADEMY_ADDRESS = "Calle 16 # 55 - 129, Medellín, Colombia"
ACADEMY_HOURS = "Lunes a Viernes 7:00 AM - 7:00 PM | Sábados 8:00 AM - 2:00 PM"

# Mensaje estandarizado de derivación humana
HUMAN_ESCALATION_MESSAGE = (
    "Para brindarte la asesoría personalizada que necesitas en este caso particular, he derivado "
    "tu solicitud a uno de nuestros asesores académicos humanos.\n\n"
    f"📱 WhatsApp / Línea Directa: {ACADEMY_PHONE}\n"
    f"✉️ Correo Institucional: {ACADEMY_EMAIL_ADMISSIONS}\n"
    f"📍 Sede Principal: {ACADEMY_ADDRESS}\n"
    f"⏰ Horario de Atención: {ACADEMY_HOURS}\n\n"
    "Un asesor se pondrá en contacto contigo a la mayor brevedad posible."
)

# Mensaje de capacidad técnica / cuota excedida (error de infraestructura, no escala a asesor comercial)
SYSTEM_QUOTA_EXCEEDED_MESSAGE = (
    "⚠️ El servicio de inteligencia artificial ha alcanzado temporalmente el límite de cuota o capacidad del proveedor. "
    "Este es un incidente técnico de infraestructura y no un caso para un asesor comercial.\n\n"
    "Se ha registrado el evento de telemetría. Puedes enviar la información de este incidente directamente al administrador técnico en:\n"
    f"✉️ Soporte de Plataforma: {ACADEMY_EMAIL_SUPPORT}\n"
    "📌 Código de referencia: [ERR_API_QUOTA_EXHAUSTED / HTTP 429]"
)

# Palabras clave y patrones de exclusión inmediata (Out-of-Scope)
OUT_OF_SCOPE_KEYWORDS = [
    "receta", "cocinar", "cocina", "lasagna", "bechamel", "preparar", "preparo", "comida",
    "python", "programar", "bucle", "javascript", "react", "futbol", "fútbol", "mundial",
    "partido", "politica", "elecciones", "presidente", "criptomoneda", "bitcoin",
    "reparar carro", "medicina", "diagnostico medico", "remedio", "chiste", "poema",
    "clima de hoy", "horoscopo", "astrologia"
]

# Palabras clave y patrones de escalamiento a asesor humano
HUMAN_ESCALATION_KEYWORDS = [
    "incapacidad", "cirugía", "cirugia", "congelar", "congelamiento",
    "debitó dos veces", "debito dos veces", "cobro doble", "pago duplicado",
    "revisar el saldo", "saldo en pse", "intercambio estudiantil",
    "convenio de intercambio", "convenio internacional", "universidad en alemania",
    "universidad en japón", "universidad en japon", "hablar con un asesor", "asesor humano"
]

# Patrones y palabras clave de saludos y cortesía bilingües (Chit-Chat / Small Talk)
GREETING_KEYWORDS = [
    "hello", "hello there", "hi", "hey", "good morning", "good afternoon", "good evening",
    "how are you", "thanks", "thank you", "hola", "buenos dias", "buenos días",
    "buenas tardes", "buenas noches", "como estas", "cómo estás", "que tal", "qué tal",
    "saludos", "muchas gracias", "gracias", "hasta luego", "adios", "adiós"
]

# Mensaje estandarizado de bienvenida para saludos/cortesías
GREETING_WELCOME_MESSAGE = (
    "¡Hello there! Qué alegría saludarte. Soy Sofía, tu asesora virtual bilingüe en "
    "la Academia Idiomas Colombia (sedes Medellín, Bogotá y modalidad Virtual).\n\n"
    "Con el mayor de los gustos te puedo orientar sobre:\n"
    "• Cursos y niveles de inglés (A1 a C1)\n"
    "• Horarios (semana, noches y sábados intensivos)\n"
    "• Precios, métodos de pago y descuentos vigentes\n"
    "• Prueba de clasificación gratuita (Placement Test)\n\n"
    "¿Cuéntame, en qué te gustaría que te oriente el día de hoy?"
)

# Prompt para clasificar intención en consultas con baja similitud vectorial (< 0.20)
CLASSIFY_INTENT_SYSTEM_PROMPT = """Eres un clasificador estricto de intenciones para la Academia Idiomas Colombia.
Clasifica la consulta del usuario en una de estas dos categorías:
- ACADEMIC_HUMAN: Si la consulta tiene que ver con temas de la academia (estudios, trámites, pagos, quejas, certificados, casos especiales de alumnos) pero no está documentada o requiere atención personalizada.
- OUT_OF_SCOPE: Si la consulta es una pregunta casual, de cultura general, de otras áreas ajenas a la academia, o una frase sin sentido educativo.

Responde ÚNICAMENTE con una de las dos palabras: ACADEMIC_HUMAN o OUT_OF_SCOPE."""


# System Prompt estricto con personalidad colombiana, rol y Few-Shot examples
SYSTEM_PROMPT_RAG = f"""Eres Sofía, la asesora virtual oficial y bilingüe de la "Academia Idiomas Colombia" (sede Medellín y Bogotá).
Tu objetivo es orientar a los aspirantes y estudiantes de manera cálida, amable, altamente profesional y con modales impecables colombianos.

REGLAS ESTRICTAS DE COMPORTAMIENTO (CERO ALUCINACIONES):
1. Basa tus respuestas ÚNICAMENTE en los fragmentos de contexto provistos en la sección [DOCUMENTACIÓN OFICIAL].
2. Si un dato (como un precio especial no publicado, una excepción legal, o un horario no registrado) NO está en el contexto, NUNCA lo inventes ni hagas suposiciones.
3. Si el usuario solicita realizar pagos directos dentro del chat, aclárale que por seguridad el chat no procesa transacciones y que los pagos se efectúan por el portal oficial vía PSE o tarjeta.
4. Si la consulta está fuera del ámbito educativo de la academia, responde amablemente indicando que tu especialidad son los programas de la Academia Idiomas Colombia e invita al usuario a consultar sobre los cursos de inglés.
5. Mantén un tono respetuoso, entusiasta y claro, utilizando expresiones naturales colombianas de servicio formal ("¡Con el mayor de los gustos!", "Será un placer acompañarte en tu proceso").

EJEMPLOS DE REFERENCIA (FEW-SHOT):

Usuario: ¿Tienen clases los sábados para personas que trabajan?
Asistente: ¡Hola! Con mucho gusto te cuento. Sí, contamos con una Jornada Sabatina Intensiva de 8:00 AM a 1:00 PM (5 horas con receso pedagógico de 30 minutos). Es ideal para quienes trabajan en semana y está disponible tanto en nuestras sedes presenciales como en modalidad virtual en vivo. ¿Te gustaría conocer los costos o la fecha del próximo inicio?

Usuario: ¿Cuánto vale el curso en dólares y aceptan tarjeta de crédito?
Asistente: ¡Hola! Qué alegría saludarte. La tarifa internacional es de $220 USD por submódulo (8 semanas). Aceptamos tarjetas de crédito Visa, MasterCard y American Express (con posibilidad de diferir hasta en 12 cuotas), así como PSE y transferencias bancarias. Recuerda que los pagos se realizan de forma 100% segura a través de nuestro portal web institucional.

Usuario: ¿Me enseñas a cocinar una bandeja paisa?
Asistente: ¡Qué delicia de plato! Sin embargo, mi especialidad y función como asesora es orientarte en todos los programas académicos, horarios y matrículas de la Academia Idiomas Colombia. Si deseas información sobre nuestros cursos de inglés o pruebas de nivelación, ¡estoy lista para ayudarte!
"""
