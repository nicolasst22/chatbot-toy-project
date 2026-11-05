from fastapi import APIRouter

from app.api.routes import bot

api_router = APIRouter()
api_router.include_router(bot.router, prefix="/bot", tags=["bot"])
