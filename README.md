# Motomex Chatbot Refacciones

Solucion tecnica para extraer un catalogo de refacciones desde texto en prosa, almacenarlo en SQLite, exponerlo por API y conectarlo con un chatbot en n8n usando IA local desde LM Studio.

## Arquitectura

- **FastAPI:** API de productos, disponibilidad y leads.
- **SQLite:** almacenamiento local del catalogo y leads.
- **LM Studio:** LLM local compatible con OpenAI para extraer intencion y entidades.
- **n8n:** orquestador del flujo conversacional.

La regla principal es que el modelo de IA no decide informacion comercial. Precios, stock, disponibilidad y compatibilidades salen de la API.

## Requisitos

- Python 3.12+
- LM Studio con servidor local activo en `http://127.0.0.1:1234/v1`
- Modelo recomendado en LM Studio para n8n: `meta-llama-3.1-8b-instruct`
- Docker para ejecutar n8n local

## Instalacion

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Variables De Entorno

Copia `.env.example` a `.env` si quieres personalizar rutas o modelos. Valores por defecto:

```env
DATABASE_URL=sqlite:///data/motomex.db
LM_STUDIO_BASE_URL=http://127.0.0.1:1234/v1
LM_STUDIO_MODEL=meta-llama-3.1-8b-instruct
API_BASE_URL=http://127.0.0.1:8000
```

## Inicializar Base De Datos

Carga el catalogo validado:

```powershell
python scripts/seed_catalog.py
```

Intentar extraccion con LM Studio y usar fallback validado si falla:

```powershell
python scripts/seed_catalog.py --use-llm
```

## Ejecutar API

```powershell
uvicorn app.main:app --reload
```

Endpoints principales:

- `GET http://127.0.0.1:8000/health`
- `GET http://127.0.0.1:8000/productos`
- `GET http://127.0.0.1:8000/productos?modelo=L-47-650`
- `GET http://127.0.0.1:8000/productos?categoria=bateria`
- `GET http://127.0.0.1:8000/disponibilidad?ciudad=Monterrey&estado=Nuevo%20Leon`
- `POST http://127.0.0.1:8000/leads`

Swagger:

```text
http://127.0.0.1:8000/docs
```

Tester web del chatbot:

```text
http://127.0.0.1:8000/tester
```

Esta pantalla permite probar los cinco casos principales sin PowerShell ni Postman. Internamente manda mensajes al webhook publicado de n8n.

## Ejecutar n8n

Opcion recomendada, persistente en segundo plano:

```powershell
docker compose up -d
```

Ver logs:

```powershell
docker logs -f n8n-motomex
```

Detener n8n sin borrar datos:

```powershell
docker compose stop
```

Volver a levantarlo:

```powershell
docker compose up -d
```

Alternativa temporal:

```powershell
docker run -it --rm --name n8n -p 5678:5678 -v n8n_data:/home/node/.n8n n8nio/n8n
```

La alternativa temporal se detiene al cerrar la terminal. Para la prueba tecnica conviene usar `docker compose up -d`.

Importa el workflow:

```text
workflows/n8n_motomex_chatbot.json
```

Despues de importarlo, activa el workflow en n8n para publicar el webhook.

Dentro del contenedor de n8n, LM Studio y la API local deben llamarse con:

- LM Studio: `http://host.docker.internal:1234/v1`
- API: `http://host.docker.internal:8000`

Webhook del workflow:

```text
POST http://localhost:5678/webhook/motomex-chatbot
```

Body de ejemplo:

```json
{
  "message": "Hola, busco una bateria para un Versa"
}
```

## Pruebas Sin WhatsApp API

No es obligatorio tener WhatsApp API para demostrar la solucion. El webhook de n8n simula el mensaje entrante que normalmente enviaria WhatsApp.

Ejemplo con PowerShell:

```powershell
Invoke-RestMethod -Uri http://localhost:5678/webhook/motomex-chatbot -Method POST -ContentType "application/json" -Body '{"message":"Hola, busco una bateria para un Versa"}'
```

Para produccion, WhatsApp Cloud API o un proveedor como Twilio, 360dialog o WATI enviaria los mensajes al mismo webhook de n8n. El resto del flujo se mantiene igual.

## Pruebas

```powershell
pytest
```

Las pruebas cubren:

- catalogo con 6 productos,
- filtros por modelo/categoria/ciudad,
- producto fuera de catalogo,
- lead incompleto,
- lead completo.

## Evidencias

- Catalogo estructurado: `data/catalogo_estructurado.json`
- Texto fuente: `data/catalog_source.txt`
- Workflow n8n: `workflows/n8n_motomex_chatbot.json`
- Conversaciones esperadas: `docs/evidencia_conversaciones.md`
- Arquitectura: `docs/architecture.md`
- Preguntas de cierre: `docs/preguntas_cierre.md`

## Modelo LLM Elegido

Modelo local recomendado para el flujo de n8n: `meta-llama-3.1-8b-instruct`.

Motivos:

- responde JSON normal en `content` sin consumir la salida en razonamiento interno,
- viable en RTX 4060 con 8 GB VRAM,
- suficiente para extraccion de entidades y clasificacion de intencion,
- compatible con LM Studio y API tipo OpenAI.

Fallback local: `ibm/granite-4-h-tiny`, que tambien respondio JSON correctamente durante las pruebas.

Si el modelo local no pasa las pruebas conversacionales, el siguiente paso seria migrar el nodo LLM de n8n a Gemini u OpenAI manteniendo igual la API y las reglas deterministas.

## Forma De Entrega

Subir este proyecto a un repositorio publico de GitHub y responder el correo de la prueba con el enlace. No subir `.env`, credenciales ni tokens.
