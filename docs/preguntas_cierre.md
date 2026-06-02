# Preguntas de Cierre

## ¿Qué riesgos existen si la IA recomienda compatibilidades incorrectas?

Puede provocar ventas equivocadas, devoluciones de producto, daños mecánicos en el vehículo del cliente, pérdida de confianza y responsabilidad civil o comercial para la empresa. Por ello, la IA solo debe mencionar compatibilidades generales obtenidas de la base de datos y solicitar siempre la validación del año/versión del vehículo, o canalizar la conversación a un asesor humano cuando exista duda.

## ¿Qué información debería venir siempre desde la API y no desde el modelo?

Toda la información transaccional y de catálogo crítico, como: precios, stock disponible, ubicación de las sucursales (ciudad/estado), compatibilidades validadas en el sistema, modelos y marcas disponibles, y condiciones de venta. El modelo de lenguaje (LLM) no debe memorizar datos numéricos ni comerciales; debe consultarlos dinámicamente desde la API.

## ¿Cómo evitarías que el chatbot invente datos?

Se previene combinando varias estrategias:
- Usando **prompts muy restrictivos** con instrucciones claras de no asumir ni inventar información técnica o comercial.
- Configurando la **temperatura en 0** en el modelo para forzar respuestas deterministas basadas en el contexto.
- Implementando **lógica determinista** (como hicimos en n8n/Python) que reciba los datos de la API y filtre/formatee la respuesta, bloqueando cualquier intento de la IA de generar precios o stock ficticios si el producto no existe en el sistema.

## ¿Cómo manejarías una conversación donde el cliente da información incompleta?

Manteniendo el estado de la sesión activo (en base de datos o en la memoria del flujo de n8n) y evaluando qué campos obligatorios del lead están vacíos. El chatbot debe capturar progresivamente la información e interrogar al cliente solicitando **únicamente** los datos pendientes (por ejemplo, preguntar por la ciudad o el año del auto si el nombre ya fue proporcionado), en lugar de volver a pedir toda la información desde el inicio.

## ¿Qué partes de tu solución escalarían bien y cuáles habría que mejorar?

- **Escala bien:** La separación arquitectónica entre el orquestador (n8n), la capa de datos/API (FastAPI) y el modelo de lenguaje (LLM local o API externa). También el almacenamiento estructurado y la lógica determinista para reglas de negocio.
- **A mejorar para producción:** Reemplazar SQLite por una base de datos más robusta (como PostgreSQL), mejorar la gestión y expiración de sesiones de chat (actualmente persistidas de manera global en n8n), añadir observabilidad (monitoreo de errores del LLM) y añadir autenticación a los endpoints de la API.

## ¿Qué cambiarías si el catálogo tuviera 10,000 productos?

- Migraría a una base de datos relacional robusta (como PostgreSQL) con índices optimizados para las búsquedas textuales de `marca`, `modelo`, `categoría` y `ciudad`.
- Implementaría **búsqueda semántica (Vector Search / RAG)** mediante embeddings para recuperar los productos candidatos más relevantes en lenguaje natural antes de pasarlos a la lógica determinista.
- Reemplazaría las comparaciones simples de texto `LIKE` por un motor de búsqueda de texto completo (Full-Text Search) o bases de datos como Elasticsearch si la carga de consultas es muy alta.

## ¿Cómo explicarías al dueño de la empresa que un sistema con IA no es completamente determinista y que, aunque puede aportar valor, necesita límites, validaciones y supervisión?

Le explicaría que un modelo de IA funciona de forma similar a un humano: es excelente interpretando la intención, el tono y la variedad de cómo escribe un cliente, pero puede cometer errores al procesar datos precisos o alucinar respuestas. Para aprovechar su valor sin poner en riesgo el negocio, la IA actúa únicamente como un "traductor" de mensajes, mientras que los cálculos de precios, las existencias reales y las confirmaciones de compra se procesan a través de sistemas informáticos tradicionales 100% confiables y verificables, con el respaldo final de un asesor de servicio para la autorización de la venta.

## ¿Qué pruebas aplicarías a este sistema impulsado por IA para asegurar al dueño de la empresa un alto nivel de confiabilidad antes de usarlo con clientes reales? Considera pruebas funcionales, casos límite, errores de integración, alucinaciones de la IA, calidad de los datos y trazabilidad de las respuestas.

- **Pruebas funcionales de API:** Asegurar mediante pruebas automatizadas (con herramientas como `pytest`) que los endpoints de consulta de catálogo y creación de leads respondan siempre con códigos correctos (200, 201) y en los formatos esperados.
- **Pruebas de flujo conversacional y casos límite:** Simular conversaciones simulando clientes enojados, que escriben con faltas de ortografía graves, mezclan múltiples intenciones o que cambian de opinión a mitad del flujo de compra.
- **Pruebas de robustez en la integración:** Validar cómo responde el chatbot si la API local falla o si el servidor de LLM se cae (definiendo respuestas de contingencia amigables como *"Por el momento no puedo procesar tu solicitud, te canalizaré con un agente"*).
- **Pruebas anti-alucinaciones:** Medir con un set de preguntas de control si el LLM inventa marcas, precios o stock que no se encuentren en la API.
- **Trazabilidad de datos:** Asegurar mediante logs que cada respuesta comercial enviada por el bot provenga directamente de una consulta válida a la base de datos, garantizando auditoría total.

## Si tuvieras más tiempo de trabajo, ¿qué mejoras implementarías para que esta solución fuera más robusta, escalable y confiable en producción?

- Integración real con la API oficial de WhatsApp Cloud API utilizando webhooks seguros y firma de verificación.
- Implementación de un panel web administrativo (Dashboard) para que los asesores humanos puedan ver en tiempo real los leads capturados y tomar el control del chat de inmediato (*human-in-the-loop*).
- Automatización de las evaluaciones de calidad del LLM (utilizando frameworks de evaluación como Ragas o Promptfoo).
- Migración a PostgreSQL e implementación de persistencia distribuida para n8n (ej. usando Redis para colas de tareas).
- Implementación de cifrado de extremo a extremo para los datos personales de los clientes guardados en la base de datos (cumplimiento de LFPDPPP).
