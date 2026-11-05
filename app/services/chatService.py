import logging
from pathlib import Path
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI, OpenAIEmbeddings  # Cliente de OpenAI
from langchain_classic.memory import ConversationSummaryBufferMemory

from app.core.config import DB_PATH, settings

from langsmith import traceable

from app.services.agents.sales import SalesAgent

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# integrador/data/chroma_db, independiente del directorio desde el que se lance la app
# CHROMA_DIR = Path(__file__).resolve().parents[2] / "data" / "chroma_db"
CHROMA_DIR = Path("data/chroma_db")
class ChatbotService:

    def __init__(self):
        self.llm = ChatOpenAI(
            model=settings.model_name,
            base_url=settings.model_url,
            api_key=settings.model_api_key,
            tiktoken_model_name="gpt-4o",
        )
        logger.info("ChatbotService inicializado")
        embeddings = OpenAIEmbeddings(openai_api_key=settings.openai_api_key)
        self.vectorstore = Chroma(
            collection_name="productos", 
            embedding_function=embeddings,
            persist_directory=str(CHROMA_DIR),
        )
        self.retriever = self.vectorstore.as_retriever(
            search_type="similarity",  # Tipo de búsqueda: similarity o mmr
            search_kwargs={"k": 20}      # Número de documentos a recuperar
        )
        self.memories: dict[str, ConversationSummaryBufferMemory] = {}
        self.salesAgent = SalesAgent(llm=self.llm, retriever=self.retriever, db=DB_PATH.as_uri()) 

    def _get_memory(self, chat_id: str) -> ConversationSummaryBufferMemory:
        if chat_id not in self.memories:
            self.memories[chat_id] = ConversationSummaryBufferMemory(
                llm=self.llm,            # el mismo LLM resume el historial viejo
                max_token_limit=5000,     # sobre este límite, los mensajes viejos se resumen
                memory_key="chat_history",
                input_key="question",
                output_key="answer",     # la chain devuelve answer + source_documents
                return_messages=True,
            )
        return self.memories[chat_id]

    @traceable
    def chat(self, userPrompt, chat_id):
        history = self._get_memory(chat_id)
        response = self.salesAgent.chat(userPrompt, history)
        print(response)
        return response
