from fastapi import APIRouter

from app.models.chatbot import ChatRequest, ChatResponse
from app.services.chatService import ChatbotService
import logging

router = APIRouter()
chatbot = ChatbotService()
logger = logging.getLogger(__name__)

@router.post("/", response_model=ChatResponse, status_code=200)
def chat(payload: ChatRequest):
    try:
        respuesta = chatbot.chat(payload.message, payload.chat_id)
    except Exception:
        logger.exception("Falló chatbot.chat (chat_id=%s)", payload.chat_id)
        respuesta = "Ha ocurrido un error. Intentalo más tarde"
        
    return {"chat_id": payload.chat_id, "response": respuesta}