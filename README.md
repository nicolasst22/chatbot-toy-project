# HW Chatbot Toy Proyect 

Chatbot de asesoría de productos de hardware: un agente de ventas (FastAPI + LangChain + ChromaDB + SQLite) que busca productos con RAG y consulta precio y stock en una base de datos.

## Cómo funciona

`POST /api/v1/bot/` → `ChatbotService` → `SalesAgent` (agente con tool calling). El LLM decide qué herramientas usar:

| Tool | Fuente | Para qué |
|---|---|---|
| `search_products` | ChromaDB (RAG, `k=20`) | Buscar productos, specs y compatibilidad. Devuelve también el SKU |
| `get_price_and_stock` | SQLite `data/db/tienda.db` (solo lectura) | Precio en USD y disponibilidad a partir del SKU |

- El precio y el stock se obtienen siempre en dos pasos: primero `search_products` (para el SKU) y después `get_price_and_stock`.
- El agente responde solo con lo que devuelven las tools, no revela la cantidad exacta en stock y rechaza temas que no sean hardware.
- La memoria es por `chat_id` (`ConversationSummaryBufferMemory`, en RAM: se pierde al reiniciar el servidor).

## Requisitos

- Entorno conda con requirements desde requirements.txt (Python 3.13, langchain 1.x...)
- Archivo `.env` en la raíz (copiar de `.env.example` y completar):

| Variable | Para qué |
|---|---|
| `MODEL_NAME`, `MODEL_URL`, `MODEL_API_KEY` | LLM del chat (OpenRouter u otro compatible con OpenAI) |
| `OPENAI_API_KEY` | Embeddings de OpenAI para buscar en Chroma (Quizas lo cambie en el futuro para operar sin dependencia de openai) |

Opcional: variables `LANGSMITH_*` en el `.env` para trazar las llamadas con LangSmith (`config.py` carga el `.env` en `os.environ` para eso).

Los datos ya están incluidos:

- `data/chroma_db/` — base vectorial de productos (colección `productos`)
- `data/db/tienda.db` — SQLite con `productos`, `categorias`, `equivalencias`, `cotizacion`, `zonas_envio` y las vistas `v_disponibles` y `v_alternativas_con_stock`
- `data/raw/productos.json` — catálogo original, solo de referencia (la app no lo lee; usa Chroma y `tienda.db`)

## Iniciar

Desde la raíz del proyecto:

```powershell
uvicorn app.main:app --reload
```

Instalar dependencias (solo la primera vez): `pip install -r requirements.txt`

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
    chatService.py             # ChatbotService: LLM, Chroma, memorias por chat_id y SalesAgent
    agents/
      sales.py                 # SalesAgent: system prompt + AgentExecutor
      tools.py                 # search_products y get_price_and_stock
  helpers/
    retriever_with_specs.py    # RetrieverWithSpecs: agrega las specs a los documentos del retriever
  core/config.py               # settings desde .env, DB_PATH
  static/chatbot.html          # UI del chat
data/
  chroma_db/                   # base vectorial de productos
  db/tienda.db                 # precios y stock
  raw/productos.json           # catálogo original (solo referencia)
```
