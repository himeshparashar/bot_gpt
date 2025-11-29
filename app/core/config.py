"""
Application Configuration - Pydantic Settings
"""
from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    """Application settings loaded from environment variables"""
    
    # App Settings
    APP_NAME: str = "Bot GPT"
    DEBUG: bool = True
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    
    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/bot_gpt"
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
