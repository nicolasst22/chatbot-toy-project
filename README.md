# HW Chatbot Toy Project

🇬🇧 English | 🇪🇸 [Español](README.es.md)

Hardware advisory chatbot with a router and two agents: sales (catalog, price, stock, currency conversion and web search) and store policies (FastAPI + LangChain + ChromaDB + SQLite + MCP server).

## How it works

`POST /api/v1/bot/` → `ChatbotService` → `AgentRouter` → `SalesAgent` or `PoliciesAgent` (tool-calling agents). Each agent's LLM decides which tools to use:

| Agent | Tool | Source | Purpose |
|---|---|---|---|
| `SalesAgent` | `search_products` | ChromaDB, `productos` collection (RAG, `k=20`) | Find products, specs and compatibility. Also returns the SKU |
| `SalesAgent` | `get_price_and_stock` | SQLite `data/db/tienda.db` (read-only) | Price in USD and availability, from the SKU |
| `SalesAgent` | `currency_exchange_rate` | Own MCP server (`mcp_products/`), which queries the [Frankfurter](https://frankfurter.dev) API | Exchange rate between two currencies (e.g. USD → ARS) to convert prices |
| `SalesAgent` | `web_search` | DuckDuckGo (falling back to Yahoo and Bing) | Search the web for a spec the bot doesn't have for a product it does know |
| `PoliciesAgent` | `search_policies` | ChromaDB, `politicas` collection (RAG, `k=5`) | Warranty, shipping, exchanges and returns, payment methods, imported products, technical service, address and opening hours |

**Router** (`app/services/router.py`): picks the agent in three layers. First by rules (sales or policy keywords); if there is no clear winner, it asks the LLM; and if that fails, it falls back to `sales`.

- Price and stock are always fetched in two steps: first `search_products` (to get the SKU), then `get_price_and_stock`.
- To quote a price in pesos, the agent gets the exchange rate with `currency_exchange_rate` (MCP), multiplies it by the USD price and states which rate it used.
- If the customer asks about a characteristic that the catalog doesn't have for a product that does exist, the sales agent looks it up on the web with `web_search`. If it can't find it either, it says it has no information (it doesn't make things up). If the search fails (blocks, 429, DNS), the bot says so instead of crashing.
- Agents answer only with what their tools return. The sales agent never reveals the exact stock quantity, and both refuse topics outside their area.
- Memory is per `chat_id` and shared between both agents (`ConversationSummaryBufferMemory`, in RAM: lost when the server restarts).

## Requirements

- Conda environment with the dependencies from requirements.txt (Python 3.13, langchain 1.x...)
- `.env` file in the project root (copy from `.env.example` and fill in):

| Variable | Purpose |
|---|---|
| `MODEL_NAME`, `MODEL_URL`, `MODEL_API_KEY` | Chat LLM (OpenRouter or any OpenAI-compatible provider) |
| `OPENAI_API_KEY` | OpenAI embeddings for searching Chroma (may change in the future to remove the OpenAI dependency) |
| `MCP_SERVER_URL` | URL of the currency-conversion MCP server (local: `http://localhost:8001/mcp`; in Docker: `http://mcp:8001/mcp`) |

Optional: `LANGSMITH_*` variables in the `.env` to trace calls with LangSmith (`config.py` loads the `.env` into `os.environ` for this).

The data is already included:

- `data/chroma_db/` — vector store with the `productos` and `politicas` collections
- `data/raw/politicas/` — policy documents (markdown), source of the `politicas` collection. Load them with `python scripts/ingest_policies.py`
- `data/raw/otros/` — supporting documents the app doesn't currently use (abbreviations glossary, stock and reservations)
- `data/db/tienda.db` — SQLite with `productos`, `categorias`, `equivalencias`, `cotizacion`, `zonas_envio` and the views `v_disponibles` and `v_alternativas_con_stock`
- `data/raw/productos.json` — original catalog, for reference only (the app doesn't read it; it uses Chroma and `tienda.db`)

## Getting started

Install dependencies (first time only): `pip install -r requirements.txt` (and `pip install -r mcp_products/requirements.txt` for the MCP server).

### Local

Two processes are needed, both from the project root. First the MCP server (port 8001), then the app:

```powershell
python mcp_products/mcp_server.py
uvicorn app.main:app --reload
```

If the MCP server isn't running, the sales agent can't initialize its tools.

### Docker

```powershell
docker compose -f docker/local/docker-compose.yml up --build
```

This starts `mcp` (port 8001) and `bot` (port 8000), which uses the `.env` in the project root and reaches the MCP server through `MCP_SERVER_URL=http://mcp:8001/mcp`.

## URLs

- `http://127.0.0.1:8000/` — chat page
- `http://127.0.0.1:8000/docs` — Swagger
- `http://127.0.0.1:8000/health` — quick health check

## API

`POST /api/v1/bot/`

```json
{ "chat_id": "user-123", "message": "Do you have motherboards with wifi?" }
```

Response:

```json
{ "chat_id": "user-123", "response": "..." }
```

## Project structure

```
app/
  main.py                      # FastAPI entry point (/health, / → chatbot.html)
  api/
    router.py                  # groups the routers
    routes/bot.py              # chat endpoint
  models/chatbot.py            # ChatRequest / ChatResponse
  services/
    chatService.py             # ChatbotService: LLM, Chroma, per-chat_id memories, router and agents
    router.py                  # AgentRouter: rules, LLM and fallback
    agents/
      sales.py                 # SalesAgent: system prompt + AgentExecutor; MCP tools and web search (DuckDuckGo)
      policies.py              # PoliciesAgent: system prompt + AgentExecutor
      tools.py                 # search_products, get_price_and_stock and search_policies
  helpers/
    retriever_with_specs.py    # RetrieverWithSpecs: adds the specs to the retriever's documents
  core/config.py               # settings from .env, DB_PATH
  static/chatbot.html          # chat UI
mcp_products/
  mcp_server.py                # MCP server (FastMCP, streamable-http, :8001): currency_exchange_rate tool
  Dockerfile, requirements.txt
docker/
  local/docker-compose.yml     # mcp + bot
Dockerfile                     # app build
scripts/ingest_policies.py     # loads data/raw/politicas into the politicas collection
tests/test_router.py           # router tests (python -m pytest)
data/
  chroma_db/                   # vector store (productos and politicas)
  db/tienda.db                 # prices and stock
  raw/productos.json           # original catalog (reference only)
  raw/politicas/               # policy documents
  raw/otros/                   # supporting documents (not used by the app)
```
