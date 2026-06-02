# Preguntas De Cierre

## Que riesgos existen si la IA recomienda compatibilidades incorrectas

Puede provocar ventas equivocadas, devoluciones, danios mecanicos, perdida de confianza y responsabilidad comercial. Por eso la IA solo debe hablar de compatibilidad general y pedir validacion de anio/version o canalizar a asesor.

## Que informacion deberia venir siempre desde la API y no desde el modelo

Precio, stock, disponibilidad por ciudad/estado, modelos disponibles, marcas, categorias, condiciones de compra y compatibilidades registradas.

## Como evitarias que el chatbot invente datos

Con prompts restrictivos, temperatura baja, respuestas basadas en API, validacion de campos, pruebas anti-alucinacion y reglas deterministas que bloqueen respuestas comerciales sin respaldo de datos.

## Como manejarias una conversacion con informacion incompleta

Manteniendo estado por cliente y preguntando solo los datos faltantes: vehiculo, anio, ciudad, estado, nombre o direccion si desea comprar.

## Que partes escalan bien y cuales habria que mejorar

Escalan bien la separacion API/n8n/LLM y el uso de datos estructurados. Habria que mejorar SQLite, busqueda textual simple, persistencia de sesion y observabilidad.

## Que cambiarias con 10,000 productos

Usaria PostgreSQL, indices, normalizacion parcial de compatibilidades, busqueda full-text, trazabilidad de fuentes y posiblemente embeddings para recuperar candidatos antes de responder.

## Como explicarias que la IA no es completamente determinista

La IA interpreta lenguaje y puede variar sus respuestas. Para usarla con seguridad, se limitan sus responsabilidades: entiende el mensaje, pero las decisiones comerciales vienen de sistemas verificables.

## Que pruebas aplicarias

Pruebas funcionales de API, pruebas de conversacion completa, casos limite, productos inexistentes, datos incompletos, errores de integracion, respuestas sin inventar datos, trazabilidad de cada respuesta hacia la API y revision de calidad del catalogo.

## Que mejoras implementarias con mas tiempo

Autenticacion, panel de leads, logs de conversacion, metricas, cola de seguimiento comercial, integracion real con WhatsApp Cloud API, base PostgreSQL y evaluacion automatizada de respuestas del LLM.
