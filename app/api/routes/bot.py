from fastapi import APIRouter

from app.models.chatbot import ChatRequest, ChatResponse
from app.services.chatService import ChatbotService

router = APIRouter()
chatbot = ChatbotService()

@router.post("/", response_model=ChatResponse, status_code=200)
def chat(payload: ChatRequest):
#    return ChatResponse(chat_id=payload.chat_id, response="hola mundo")
    # respuesta = chatbot.chat(payload.message)
    respuesta = chatbot.chat(payload.message, payload.chat_id)
    return {"chat_id": payload.chat_id, "response": respuesta}