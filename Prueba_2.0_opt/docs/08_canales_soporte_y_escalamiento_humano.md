# Academia Idiomas Colombia — Documento Oficial 08
## Canales de Atención y Protocolo de Escalamiento Humano

### 1. Rol del Asistente Virtual y Alcance
El asistente virtual inteligente está entrenado y autorizado exclusivamente para brindar información verídica, ágil y precisa basada en los documentos institucionales oficiales (horarios, sedes, precios, metodología, matrículas, exámenes y políticas).
- **Límites de Operación:** El asistente no inventa promociones no autorizadas, no altera notas académicas ni gestiona reclamos disciplinarios o legales de manera directa.

### 2. Criterios para Escalamiento a Asesor Humano
El sistema debe activar inmediatamente la bandera de escalamiento humano (`escalar_humano: true`) ante las siguientes situaciones:
1. **Consultas Fuera de Alcance (Out-of-Scope):** Preguntas de temas no relacionados con la oferta académica (ej. política general, programación informática, recetas de cocina, opiniones personales).
2. **Casos Administrativos Complejos:** Solicitudes de convenios corporativos para empresas con más de 20 empleados, quejas formales sobre docentes o trámites de devolución de dinero.
3. **Casos Médicos o Fuerza Mayor:** Solicitudes de congelamiento o incapacidades médicas prolongadas.
4. **Baja Confianza Semántica:** Cuando la consulta académica no encuentre suficiente coincidencia documental (score de similitud $< 0.20$).

### 3. Canales Oficiales de Contacto Humano
Cuando una consulta se escala a un asesor humano, se le proporciona al usuario los siguientes canales directos de atención:
- **Línea WhatsApp y Llamadas:** +57 301 732 5327 (Atención directa con el equipo de admisiones y servicio al estudiante).
- **Correo Electrónico de Admisiones:** `admisiones@idiomascolombia.edu.co`
- **Correo de Soporte Académico:** `soporte@idiomascolombia.edu.co`
- **Dirección Sede Principal:** Calle 16 # 55 - 129, Medellín, Colombia.
- **Horarios de Atención Humana:**
  - Lunes a Viernes: 07:00 AM a 07:00 PM (Jornada continua).
  - Sábados: 08:00 AM a 02:00 PM.
  - Domingos y Festivos: No hay atención presencial ni telefónica; las solicitudes se gestionan el siguiente día hábil.
