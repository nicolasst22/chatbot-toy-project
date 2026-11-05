import logging
import os

from fastapi import FastAPI
from fastapi.responses import HTMLResponse

from app.api.router import api_router
from app.core.config import settings

logging.basicConfig(level=logging.INFO)

app = FastAPI(title=settings.project_name)
app.include_router(api_router, prefix=settings.api_prefix)

@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
async def read_root():
    print("Current Directory:", os.getcwd())
    with open("./app/static/chatbot.html", "r", encoding="utf-8") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content, status_code=200)
