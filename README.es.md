# HW Chatbot Toy Project

🇬🇧 [English](README.md) | 🇪🇸 Español

Chatbot de asesoría de hardware con un router y dos agentes: ventas (catálogo, precio, stock, cotización de monedas y búsqueda web) y políticas de la tienda (FastAPI + LangChain + ChromaDB + SQLite + servidor MCP).

## Cómo funciona

`POST /api/v1/bot/` → `ChatbotService` → `AgentRouter` → `SalesAgent` o `PoliciesAgent` (agentes con tool calling). El LLM de cada agente decide qué herramientas usar:

| Agente | Tool | Fuente | Para qué |
|---|---|---|---|
| `SalesAgent` | `search_products` | ChromaDB, colección `productos` (RAG, `k=20`) | Buscar productos, specs y compatibilidad. Devuelve también el SKU |
| `SalesAgent` | `get_price_and_stock` | SQLite `data/db/tienda.db` (solo lectura) | Precio en USD y disponibilidad a partir del SKU |
| `SalesAgent` | `currency_exchange_rate` | Servidor MCP propio (`mcp_products/`), que consulta la API de [Frankfurter](https://frankfurter.dev) | Tipo de cambio entre dos monedas (ej. USD → ARS) para convertir los precios |
| `SalesAgent` | `web_search` | DuckDuckGo (con respaldo en Yahoo y Bing) | Buscar en internet una spec que el bot no tiene de un producto que sí conoce |
| `PoliciesAgent` | `search_policies` | ChromaDB, colección `politicas` (RAG, `k=5`) | Garantía, envíos, cambios y devoluciones, medios de pago, productos importados, servicio técnico, dirección y horarios |

**Router** (`app/services/router.py`): elige el agente en tres capas. Primero por reglas (palabras clave de ventas o de políticas); si no hay un ganador claro, le pregunta al LLM; y si eso falla, usa `sales` como respaldo.

- El precio y el stock se obtienen siempre en dos pasos: primero `search_products` (para el SKU) y después `get_price_and_stock`.
- Para cotizar en pesos, el agente obtiene el tipo de cambio con `currency_exchange_rate` (MCP), multiplica por el precio en USD e indica qué tipo de cambio usó.
- Si el cliente pregunta una característica que el catálogo no tiene de un producto que sí existe, el agente de ventas la busca en internet con `web_search`. Si tampoco la encuentra, dice que no tiene información (no inventa). Si la búsqueda falla (bloqueos, 429, DNS), el bot lo informa en vez de romperse.
- Los agentes responden solo con lo que devuelven sus tools. El de ventas no revela la cantidad exacta en stock y ambos rechazan temas fuera de su área.
- La memoria es por `chat_id` y se comparte entre ambos agentes (`ConversationSummaryBufferMemory`, en RAM: se pierde al reiniciar el servidor).

## Requisitos

- Entorno conda con requirements desde requirements.txt (Python 3.13, langchain 1.x...)
- Archivo `.env` en la raíz (copiar de `.env.example` y completar):

| Variable | Para qué |
|---|---|
| `MODEL_NAME`, `MODEL_URL`, `MODEL_API_KEY` | LLM del chat (OpenRouter u otro compatible con OpenAI) |
| `OPENAI_API_KEY` | Embeddings de OpenAI para buscar en Chroma (Quizas lo cambie en el futuro para operar sin dependencia de openai) |
| `MCP_SERVER_URL` | URL del servidor MCP de conversión de monedas (local: `http://localhost:8001/mcp`; en Docker: `http://mcp:8001/mcp`) |

Opcional: variables `LANGSMITH_*` en el `.env` para trazar las llamadas con LangSmith (`config.py` carga el `.env` en `os.environ` para eso).

Los datos ya están incluidos:

- `data/chroma_db/` — base vectorial con las colecciones `productos` y `politicas`
- `data/raw/politicas/` — documentos de políticas (markdown), origen de la colección `politicas`. Se cargan con `python scripts/ingest_policies.py`
- `data/raw/otros/` — documentos de apoyo que hoy no usa la app (glosario de abreviaturas, stock y reservas)
- `data/db/tienda.db` — SQLite con `productos`, `categorias`, `equivalencias`, `cotizacion`, `zonas_envio` y las vistas `v_disponibles` y `v_alternativas_con_stock`
- `data/raw/productos.json` — catálogo original, solo de referencia (la app no lo lee; usa Chroma y `tienda.db`)

## Iniciar

Instalar dependencias (solo la primera vez): `pip install -r requirements.txt` (y `pip install -r mcp_products/requirements.txt` para el servidor MCP).

### Local

Hacen falta dos procesos, desde la raíz del proyecto. Primero el servidor MCP (puerto 8001) y después la app:

```powershell
python mcp_products/mcp_server.py
uvicorn app.main:app --reload
```

Si el servidor MCP no está levantado, el agente de ventas no puede inicializar sus tools.

### Docker

```powershell
docker compose -f docker/local/docker-compose.yml up --build
```

Levanta `mcp` (puerto 8001) y `bot` (puerto 8000), que usa el `.env` de la raíz y apunta al MCP con `MCP_SERVER_URL=http://mcp:8001/mcp`.

## URLs

- `http://127.0.0.1:8000/` — página del chat
- `http://127.0.0.1:8000/docs` — Swagger
- `http://127.0.0.1:8000/health` — chequeo rápido

## API

`POST /api/v1/bot/`

```json
{ "chat_id": "user-123", "message": "¿Tenés motherboards con wifi?" }
```

Respuesta:

```json
{ "chat_id": "user-123", "response": "..." }
```

## Estructura

```
app/
  main.py                      # entrada FastAPI (/health, / → chatbot.html)
  api/
    router.py                  # agrupa los routers
    routes/bot.py              # endpoint del chat
  models/chatbot.py            # ChatRequest / ChatResponse
  services/
    chatService.py             # ChatbotService: LLM, Chroma, memorias por chat_id, router y agentes
    router.py                  # AgentRouter: reglas, LLM y respaldo
    agents/
      sales.py                 # SalesAgent: system prompt + AgentExecutor; tools MCP y búsqueda web (DuckDuckGo)
      policies.py              # PoliciesAgent: system prompt + AgentExecutor
      tools.py                 # search_products, get_price_and_stock y search_policies
  helpers/
    retriever_with_specs.py    # RetrieverWithSpecs: agrega las specs a los documentos del retriever
  core/config.py               # settings desde .env, DB_PATH
  static/chatbot.html          # UI del chat
mcp_products/
  mcp_server.py                # servidor MCP (FastMCP, streamable-http, :8001): tool currency_exchange_rate
  Dockerfile, requirements.txt
docker/
  local/docker-compose.yml     # mcp + bot
Dockerfile                     # build de la app
scripts/ingest_policies.py     # carga data/raw/politicas en la colección politicas
tests/test_router.py           # tests del router (python -m pytest)
data/
  chroma_db/                   # base vectorial (productos y politicas)
  db/tienda.db                 # precios y stock
  raw/productos.json           # catálogo original (solo referencia)
  raw/politicas/               # documentos de políticas
  raw/otros/                   # documentos de apoyo (no usados por la app)
```
