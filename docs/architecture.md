# Arquitectura del Sistema

La solución implementada separa rigurosamente la **interpretación conversacional** de la **lógica comercial**. El modelo de lenguaje (LLM) local se utiliza exclusivamente para comprender los mensajes del cliente y extraer intenciones y entidades, mientras que la API y la base de datos controlan con total exactitud qué productos existen, sus precios reales, su ubicación física y su stock disponible.

---

## Componentes del Sistema

1. **FastAPI (API de Negocio):**
   * Expone los endpoints principales `/productos`, `/disponibilidad` y `/leads` necesarios para el flujo comercial.
   * Cuenta con un probador web interactivo premium en `/tester` para facilitar la simulación y validación de casos de prueba.

2. **SQLite (Base de Datos):**
   * Almacena de forma relacional el catálogo de refacciones estructurado y el registro histórico de leads de clientes.
   * Utiliza la función personalizada `remove_accents` para que todas las búsquedas sean insensibles a los acentos en español.

3. **Script de Inicialización (`seed_catalog.py`):**
   * Transforma el texto fuente en prosa a datos JSON estructurados y validados con Pydantic.
   * Soporta extracción asistida por IA local con el argumento `--use-llm` o mediante un catálogo de respaldo validado para asegurar reproducibilidad.

4. **n8n (Orquestador del Chatbot):**
   * Gestiona el flujo conversacional, enruta los mensajes entrantes, coordina las llamadas al LLM local para clasificar intenciones y conecta con la API de FastAPI.

5. **LM Studio (Servidor de IA):**
   * Provee la inferencia del modelo de lenguaje local (configurado con `meta-llama-3.1-8b-instruct`), simulando una integración de bajo costo y alta privacidad.

---

## Límites de la Inteligencia Artificial

La IA **no tiene permitido inventar ni adivinar** precios, existencias en stock, ubicaciones de sucursales ni compatibilidades técnicas avanzadas. Si un producto no se encuentra disponible en la API:
* El chatbot responde de forma determinista indicando que no encontró el producto en el catálogo.
* Ofrece registrar los datos personales del cliente para que un asesor humano lo asista.

La compatibilidad de las piezas se maneja en el catálogo como **"general"** debido a las limitaciones del texto fuente (el cual carece de especificaciones precisas como el año o motor exacto para todas las refacciones). Cuando el cliente solicita continuar con la compra, el flujo en n8n captura la dirección de envío y marca el lead como completo para que sea validado manualmente por un asesor experto antes de procesar el pedido físico.

---

## Escalabilidad del Sistema

Para escalar este prototipo a un entorno de producción real con **10,000 o más productos**, se sugieren las siguientes mejoras estructurales:
* **Base de Datos:** Migrar de SQLite a PostgreSQL e implementar índices compuestos sobre las columnas `marca`, `modelo`, `categoría` y `ciudad`.
* **Motor de Búsqueda:** Reemplazar las búsquedas simples por texto `LIKE` con un motor de búsqueda avanzada como PostgreSQL Full-Text Search o Elasticsearch.
* **Búsqueda Semántica:** Incorporar un modelo de Embeddings para realizar búsquedas vectoriales y recuperar de forma semántica las refacciones candidatas más óptimas según el lenguaje natural del cliente.
