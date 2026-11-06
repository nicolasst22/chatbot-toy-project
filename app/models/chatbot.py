from pydantic import BaseModel, Field

# Modelo de datos para las peticiones del chatbot
# Pydantic valida automáticamente que los datos recibidos cumplan con este esquema
class ChatRequest(BaseModel):
    """
    Modelo que representa una petición al chatbot
    
    Atributos:
        chat_id: Identificador único de la conversación (permite múltiples sesiones simultáneas)
        message: El mensaje o pregunta del usuario
    """
    chat_id: str  # ID de la conversación (ej: "user-123", "session-abc")
    message: str = Field(max_length=1000)  # Pregunta o mensaje del usuario (ej: "¿Tienes sofás?")

# Modelo de datos para las respuestas del chatbot
class ChatResponse(BaseModel):
    """
    Modelo que representa la respuesta del chatbot
    
    Atributos:
        chat_id: El mismo identificador de la conversación (para rastrear la respuesta)
        response: La respuesta generada por el chatbot
    """
    chat_id: str  # ID de la conversación (mismo que el de la petición)
    response: str  # Respuesta generada por el chatbot (ej: "Sí, tenemos varios sofás disponibles...")

