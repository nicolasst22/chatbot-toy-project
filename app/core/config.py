from pathlib import Path

from dotenv import load_dotenv
from pydantic_settings import BaseSettings, SettingsConfigDict

load_dotenv()

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "db" / "tienda.db"
# DB_PATH = Path("data/db/tienda.db")

DEV_ENV = 'development' 

class Settings(BaseSettings):
    project_name: str = "HW Chatbot Toy project"
    api_prefix: str = "/api/v1"

    # no default values. From .env
    model_name: str
    model_url: str
    model_api_key: str
    openai_api_key: str
    environment: str = "production"

    model_config = SettingsConfigDict(
        env_file=".env", protected_namespaces=(), extra="ignore"
    )


settings = Settings()
