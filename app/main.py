from contextlib import asynccontextmanager
import json
import urllib.error
import urllib.request

from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import HTMLResponse

from app.config import get_n8n_webhook_url
from app.database import db_session, init_db
from app.repository import create_lead, get_product, list_leads, list_products
from app.schemas import ChatMessage, Lead, LeadCreate, Product


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    yield


app = FastAPI(
    title="Motomex Refacciones API",
    description="API para catalogo de refacciones y registro de leads del chatbot.",
    version="1.0.0",
    lifespan=lifespan,
)


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/productos", response_model=list[Product])
def productos(
    modelo: str | None = None,
    marca: str | None = None,
    categoria: str | None = None,
    ciudad: str | None = None,
    estado: str | None = None,
    q: str | None = Query(default=None, description="Busqueda textual simple."),
) -> list[dict]:
    with db_session() as conn:
        return list_products(
            conn,
            modelo=modelo,
            marca=marca,
            categoria=categoria,
            ciudad=ciudad,
            estado=estado,
            q=q,
        )


@app.get("/productos/{product_id}", response_model=Product)
def producto(product_id: int) -> dict:
    with db_session() as conn:
        item = get_product(conn, product_id)
    if not item:
        raise HTTPException(status_code=404, detail="Producto no encontrado")
    return item


@app.get("/disponibilidad", response_model=list[Product])
def disponibilidad(
    ciudad: str,
    estado: str,
    modelo: str | None = None,
    marca: str | None = None,
    categoria: str | None = None,
) -> list[dict]:
    with db_session() as conn:
        products = list_products(
            conn,
            ciudad=ciudad,
            estado=estado,
            modelo=modelo,
            marca=marca,
            categoria=categoria,
        )
    return [product for product in products if product["stock"] > 0]


@app.post("/leads", response_model=Lead, status_code=201)
def registrar_lead(lead: LeadCreate) -> dict:
    with db_session() as conn:
        return create_lead(conn, lead)


@app.get("/leads", response_model=list[Lead])
def leads() -> list[dict]:
    with db_session() as conn:
        return list_leads(conn)


@app.get("/tester", response_class=HTMLResponse)
def tester() -> str:
    return """
<!doctype html>
<html lang="es">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Motomex | Chatbot Refacciones Tester</title>
  <!-- Modern Fonts -->
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700&family=Plus+Jakarta+Sans:wght@400;500;600;700&display=swap" rel="stylesheet">
  <style>
    :root {
      --bg: #0b111e;
      --card-bg: rgba(22, 30, 49, 0.75);
      --border: rgba(255, 255, 255, 0.08);
      --border-hover: rgba(59, 130, 246, 0.4);
      --text: #f3f4f6;
      --text-muted: #9ca3af;
      --primary: #2563eb;
      --primary-hover: #1d4ed8;
      --success: #10b981;
      --warning: #f59e0b;
      --danger: #ef4444;
      --accent-glow: rgba(37, 99, 235, 0.15);
    }
    
    body {
      margin: 0;
      font-family: 'Plus Jakarta Sans', sans-serif;
      background-color: var(--bg);
      background-image: 
        radial-gradient(at 10% 20%, rgba(37, 99, 235, 0.1) 0px, transparent 50%),
        radial-gradient(at 90% 80%, rgba(16, 185, 129, 0.06) 0px, transparent 50%);
      color: var(--text);
      min-height: 100vh;
      display: flex;
      flex-direction: column;
    }

    main {
      max-width: 1200px;
      width: 95%;
      margin: 40px auto;
      padding: 0 16px;
      box-sizing: border-box;
    }

    .header-bar {
      display: flex;
      justify-content: space-between;
      align-items: center;
      margin-bottom: 24px;
      border-bottom: 1px solid var(--border);
      padding-bottom: 16px;
    }

    h1 {
      font-family: 'Outfit', sans-serif;
      font-size: 28px;
      font-weight: 700;
      margin: 0;
      background: linear-gradient(135deg, #ffffff 40%, #93c5fd 100%);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      letter-spacing: -0.02em;
    }

    .subtitle {
      font-size: 13px;
      color: var(--text-muted);
      margin-top: 4px;
    }

    .layout {
      display: grid;
      grid-template-columns: 280px minmax(0, 1fr) 340px;
      gap: 20px;
      align-items: start;
    }

    .panel, .chat, .trace {
      background: var(--card-bg);
      backdrop-filter: blur(12px);
      -webkit-backdrop-filter: blur(12px);
      border: 1px solid var(--border);
      border-radius: 16px;
      box-shadow: 0 10px 30px rgba(0, 0, 0, 0.3);
      overflow: hidden;
      transition: border-color 0.3s ease, box-shadow 0.3s ease;
    }

    .panel:hover, .chat:hover, .trace:hover {
      border-color: rgba(255, 255, 255, 0.12);
    }

    /* Panel Izquierdo - Casos de Prueba */
    .panel {
      padding: 20px;
    }

    .panel strong {
      display: block;
      font-family: 'Outfit', sans-serif;
      font-size: 14px;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      margin-bottom: 14px;
    }

    .panel button {
      width: 100%;
      margin: 8px 0;
      padding: 12px 14px;
      text-align: left;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.02);
      color: var(--text);
      border-radius: 10px;
      cursor: pointer;
      font-size: 13px;
      line-height: 1.4;
      font-family: inherit;
      transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
    }

    .panel button:hover {
      background: rgba(59, 130, 246, 0.1);
      border-color: var(--border-hover);
      transform: translateY(-1px);
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.15);
    }

    .panel button:active {
      transform: translateY(0);
    }

    #clear {
      margin-top: 20px;
      background: rgba(239, 68, 68, 0.1);
      border-color: rgba(239, 68, 68, 0.2);
      color: #fca5a5;
      text-align: center;
      font-weight: 500;
    }

    #clear:hover {
      background: rgba(239, 68, 68, 0.2);
      border-color: rgba(239, 68, 68, 0.4);
      box-shadow: 0 4px 12px rgba(239, 68, 68, 0.15);
    }

    /* Panel Central - Chat */
    .chat {
      display: flex;
      flex-direction: column;
      height: 600px;
    }

    .messages {
      flex: 1;
      overflow-y: auto;
      padding: 20px;
      display: flex;
      flex-direction: column;
      gap: 16px;
    }

    /* Scrollbar Personalizada */
    .messages::-webkit-scrollbar, .trace-list::-webkit-scrollbar {
      width: 6px;
    }
    .messages::-webkit-scrollbar-track, .trace-list::-webkit-scrollbar-track {
      background: transparent;
    }
    .messages::-webkit-scrollbar-thumb, .trace-list::-webkit-scrollbar-thumb {
      background: rgba(255, 255, 255, 0.1);
      border-radius: 4px;
    }
    .messages::-webkit-scrollbar-thumb:hover, .trace-list::-webkit-scrollbar-thumb:hover {
      background: rgba(255, 255, 255, 0.25);
    }

    .msg {
      max-width: 75%;
      padding: 14px 16px;
      border-radius: 14px;
      font-size: 14px;
      line-height: 1.5;
      white-space: pre-wrap;
      animation: fadeInMessage 0.3s cubic-bezier(0.4, 0, 0.2, 1) forwards;
    }

    @keyframes fadeInMessage {
      from { opacity: 0; transform: translateY(8px); }
      to { opacity: 1; transform: translateY(0); }
    }

    .user {
      background: var(--primary);
      color: #ffffff;
      align-self: flex-end;
      border-bottom-right-radius: 2px;
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.2);
    }

    .bot {
      background: rgba(255, 255, 255, 0.05);
      border: 1px solid var(--border);
      color: var(--text);
      align-self: flex-start;
      border-bottom-left-radius: 2px;
    }

    .msg pre {
      margin: 10px 0 0;
      background: #070b13;
      border: 1px solid rgba(255, 255, 255, 0.05);
      color: #93c5fd;
      padding: 12px;
      border-radius: 8px;
      overflow-x: auto;
      font-size: 11px;
      font-family: 'Courier New', Courier, monospace;
    }

    form {
      display: flex;
      gap: 10px;
      border-top: 1px solid var(--border);
      padding: 16px;
      background: rgba(0, 0, 0, 0.15);
    }

    input {
      flex: 1;
      padding: 14px 16px;
      border: 1px solid var(--border);
      background: rgba(255, 255, 255, 0.02);
      color: var(--text);
      border-radius: 10px;
      font-size: 14px;
      font-family: inherit;
      outline: none;
      transition: all 0.2s ease;
    }

    input:focus {
      background: rgba(255, 255, 255, 0.04);
      border-color: var(--primary);
      box-shadow: 0 0 0 3px rgba(37, 99, 235, 0.15);
    }

    form button {
      padding: 0 20px;
      border: 0;
      background: var(--primary);
      color: #ffffff;
      font-weight: 600;
      font-size: 14px;
      border-radius: 10px;
      cursor: pointer;
      font-family: inherit;
      transition: all 0.2s ease;
    }

    form button:hover {
      background: var(--primary-hover);
      box-shadow: 0 4px 12px rgba(37, 99, 235, 0.25);
    }

    /* Panel Derecho - Trazabilidad */
    .trace {
      padding: 20px;
      max-height: 600px;
      display: flex;
      flex-direction: column;
    }

    .trace h2 {
      font-family: 'Outfit', sans-serif;
      font-size: 16px;
      font-weight: 600;
      margin: 0 0 16px;
      color: var(--text);
      text-transform: uppercase;
      letter-spacing: 0.05em;
    }

    .trace-block {
      border-top: 1px solid var(--border);
      padding: 14px 0;
    }

    .trace-block:first-of-type {
      border-top: 0;
      padding-top: 0;
    }

    .trace-block strong {
      display: block;
      font-size: 12px;
      margin-bottom: 8px;
      color: var(--text-muted);
      text-transform: uppercase;
      letter-spacing: 0.03em;
    }

    .trace-list {
      margin: 0;
      padding-left: 16px;
      font-size: 13px;
      line-height: 1.5;
      color: var(--text);
    }

    .trace-list li {
      margin-bottom: 4px;
    }

    .empty {
      color: var(--text-muted);
      font-size: 13px;
      font-style: italic;
    }

    .badge {
      display: inline-block;
      padding: 3px 10px;
      border-radius: 20px;
      font-size: 11px;
      font-weight: 600;
      text-transform: uppercase;
      letter-spacing: 0.02em;
    }

    .complete {
      background: rgba(16, 185, 129, 0.12);
      border: 1px solid rgba(16, 185, 129, 0.3);
      color: #a7f3d0;
    }

    .incomplete {
      background: rgba(245, 158, 11, 0.12);
      border: 1px solid rgba(245, 158, 11, 0.3);
      color: #fde68a;
    }

    #lead-state {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 12px;
      margin-top: 4px;
    }

    /* Responsividad */
    @media (max-width: 1024px) {
      .layout {
        grid-template-columns: 1fr;
      }
      .chat {
        height: 500px;
      }
      .trace {
        max-height: none;
      }
      .msg {
        max-width: 90%;
      }
    }
  </style>
</head>
<body>
  <main>
    <div class="header-bar">
      <div>
        <h1>Motomex Chatbot Tester</h1>
        <div class="subtitle">Consola de pruebas e inspección para la extracción de leads en tiempo real.</div>
      </div>
    </div>
    
    <div class="layout">
      <section class="panel">
        <strong>Casos de prueba</strong>
        <button type="button" data-message="Hola, busco una bateria para un Versa.">1. Batería para Versa</button>
        <button type="button" data-message="Soy Carlos, estoy en Monterrey, Nuevo Leon. Mi Versa es 2020.">2. Cliente da datos</button>
        <button type="button" data-message="Soy Carlos, estoy en Monterrey, Nuevo Leon. Mi Versa es 2020. Si, quiero comprar la bateria LTH L-47-650. Mi direccion es Av. Universidad 123, Colonia Centro, Monterrey, Nuevo Leon, C.P. 64000.">3. Compra completa</button>
        <button type="button" data-message="Necesito unas balatas.">4. Producto ambiguo</button>
        <button type="button" data-message="Tienen filtro de aceite para March">5. Fuera de catálogo</button>
        <button type="button" id="clear">Nueva conversación</button>
      </section>
      
      <section class="chat">
        <div id="messages" class="messages"></div>
        <form id="form">
          <input id="message" autocomplete="off" placeholder="Escribe un mensaje de cliente..." />
          <button type="submit">Enviar</button>
        </form>
      </section>
      
      <aside class="trace">
        <h2>Trazabilidad del caso</h2>
        
        <div class="trace-block">
          <strong>Datos identificados</strong>
          <ul id="identified" class="trace-list"></ul>
        </div>
        
        <div class="trace-block">
          <strong>Información consultada</strong>
          <div id="consulted" class="empty">Sin consulta todavía.</div>
        </div>
        
        <div class="trace-block">
          <strong>Decisión tomada</strong>
          <div id="decision" class="empty">Sin decisión todavía.</div>
        </div>
        
        <div class="trace-block">
          <strong>Datos pendientes</strong>
          <ul id="pending" class="trace-list"></ul>
        </div>
        
        <div class="trace-block">
          <strong>Estado del lead</strong>
          <div id="lead-state" class="empty">Sin lead registrado.</div>
        </div>
      </aside>
    </div>
  </main>

  <script>
    let currentSessionId = "web-" + Math.random().toString(36).substring(2, 9);
    const messages = document.querySelector("#messages");
    const input = document.querySelector("#message");
    const form = document.querySelector("#form");
    const history = [];
    const identified = document.querySelector("#identified");
    const consulted = document.querySelector("#consulted");
    const decision = document.querySelector("#decision");
    const pending = document.querySelector("#pending");
    const leadState = document.querySelector("#lead-state");

    const leadLabels = {
      nombre: "Nombre",
      ciudad: "Ciudad",
      estado: "Estado",
      producto_interes: "Producto de interes",
      vehiculo: "Vehiculo",
      anio_vehiculo: "Anio del vehiculo",
      direccion_envio: "Direccion de envio"
    };

    function renderList(element, rows, emptyText) {
      element.innerHTML = "";
      if (!rows.length) {
        const li = document.createElement("li");
        li.className = "empty";
        li.textContent = emptyText;
        element.appendChild(li);
        return;
      }
      rows.forEach((row) => {
        const li = document.createElement("li");
        li.textContent = row;
        element.appendChild(li);
      });
    }

    function inferDecision(reply, lead) {
      const text = (reply || "").toLowerCase();
      if (lead && lead.lead_completo) return "Lead completo registrado para seguimiento/cierre.";
      if (text.includes("no encontre")) return "Producto fuera de catalogo; se registra solicitud para asesor.";
      if (text.includes("para ayudarte mejor") || text.includes("para validar mejor")) return "Faltan datos; el bot pregunta solo lo pendiente.";
      if (text.includes("disponible") && text.includes("precio")) return "Producto encontrado; se informa disponibilidad/precio desde API.";
      return reply ? "Respuesta generada segun reglas del flujo." : "Sin decision todavia.";
    }

    function updateTrace(data) {
      const lead = data.lead || {};
      const captured = Object.entries(leadLabels)
        .filter(([key]) => lead[key])
        .map(([key, label]) => `${label}: ${lead[key]}`);
      renderList(identified, captured, "Sin datos identificados todavia.");

      const consultedText = lead.producto_interes
        ? `Catalogo/API: ${lead.producto_interes}${lead.ciudad ? ` en ${lead.ciudad}, ${lead.estado || ""}` : ""}`
        : "Sin producto consultado todavia.";
      consulted.className = lead.producto_interes ? "" : "empty";
      consulted.textContent = consultedText;

      decision.className = "";
      decision.textContent = inferDecision(data.reply, lead);

      const required = ["nombre", "ciudad", "estado", "producto_interes", "vehiculo", "anio_vehiculo"];
      if (String(data.reply || "").toLowerCase().includes("direccion") || lead.direccion_envio) {
        required.push("direccion_envio");
      }
      const missing = required
        .filter((key) => !lead[key])
        .map((key) => leadLabels[key]);
      renderList(pending, missing, "No hay datos pendientes para este paso.");

      if (lead.id) {
        leadState.innerHTML = "";
        const badge = document.createElement("span");
        badge.className = `badge ${lead.lead_completo ? "complete" : "incomplete"}`;
        badge.textContent = lead.lead_completo ? "Completo" : "Incompleto";
        leadState.appendChild(badge);
        leadState.append(` ID ${lead.id} - sesion ${lead.session_id || "sin session_id"}`);
      } else {
        leadState.className = "empty";
        leadState.textContent = "Sin lead registrado.";
      }
    }

    function addMessage(kind, text, raw) {
      const div = document.createElement("div");
      div.className = `msg ${kind}`;
      div.textContent = text;
      if (raw) {
        const pre = document.createElement("pre");
        pre.textContent = JSON.stringify(raw, null, 2);
        div.appendChild(pre);
      }
      messages.appendChild(div);
      messages.scrollTop = messages.scrollHeight;
    }

    async function send(message) {
      addMessage("user", message);
      input.value = "";
      try {
        const response = await fetch("/tester/message", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify({ message, history, session_id: currentSessionId })
        });
        const data = await response.json();
        addMessage("bot", data.reply || "(sin respuesta)", data);
        updateTrace(data);
        history.push({ role: "user", content: message });
        history.push({ role: "assistant", content: data.reply || "" });
      } catch (error) {
        addMessage("bot", `Error: ${error.message}`);
      }
    }

    form.addEventListener("submit", (event) => {
      event.preventDefault();
      const message = input.value.trim();
      if (message) send(message);
    });

    document.querySelectorAll("[data-message]").forEach((button) => {
      button.addEventListener("click", () => send(button.dataset.message));
    });

    document.querySelector("#clear").addEventListener("click", () => {
      currentSessionId = "web-" + Math.random().toString(36).substring(2, 9);
      history.length = 0;
      messages.innerHTML = "";
      updateTrace({});
      input.focus();
    });

    updateTrace({});
  </script>
</body>
</html>
"""


@app.post("/tester/message")
def tester_message(payload: ChatMessage) -> dict:
    recent_history = [item for item in payload.history if item.get("role") == "user"][-6:]
    if recent_history:
        context = "\n".join(
            f"- {item.get('content', '')}" for item in recent_history
        )
        message = (
            "Mensajes anteriores del cliente:\n"
            f"{context}\n\n"
            "Nuevo mensaje del cliente:\n"
            f"{payload.message}"
        )
    else:
        message = payload.message
    body_dict = {"message": message}
    if payload.session_id:
        body_dict["session_id"] = payload.session_id
    body = json.dumps(body_dict).encode("utf-8")
    request = urllib.request.Request(
        get_n8n_webhook_url(),
        data=body,
        headers={"Content-Type": "application/json; charset=utf-8"},
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=120) as response:
            content = response.read().decode("utf-8")
    except urllib.error.URLError as exc:
        raise HTTPException(status_code=502, detail=f"No se pudo conectar con n8n: {exc}") from exc
    return json.loads(content) if content else {"reply": "", "lead": None}
