# backend/app/settings.py
from pydantic_settings import BaseSettings

# =================================================================================
# 2. CONFIGURATION & APP INITIALIZATION
# =================================================================================

class Settings(BaseSettings):
    chroma_db_host: str
    chroma_db_port: int
    ollama_base_url: str
    # We can add more config here later

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8'

settings = Settings()