from pydantic_settings import BaseSettings
from typing import Optional


class Settings(BaseSettings):
    
    # App Settings
    APP_NAME: str = "Bot GPT"
    DEBUG: bool = True
    
    # API Keys
    OPENAI_API_KEY: Optional[str] = None
    GROQ_API_KEY: Optional[str] = None
    GOOGLE_API_KEY: Optional[str] = None
    
    # Database - PostgreSQL for Docker
    POSTGRES_USER: str = "postgres"
    POSTGRES_PASSWORD: str = "postgres"
    POSTGRES_DB: str = "bot_gpt"
    POSTGRES_HOST: str = "db"  # Docker service name
    POSTGRES_PORT: int = 5432
    
    @property
    def DATABASE_URL(self) -> str:
        return f"postgresql://{self.POSTGRES_USER}:{self.POSTGRES_PASSWORD}@{self.POSTGRES_HOST}:{self.POSTGRES_PORT}/{self.POSTGRES_DB}"
    
    # LLM Settings
    DEFAULT_LLM_PROVIDER: str = "gemini"  # gemini, groq, or openai
    DEFAULT_MODEL: str = "gemini-1.5-flash"
    
    # Context Management Settings
    MAX_CONTEXT_TOKENS: int = 4096
    MAX_RESPONSE_TOKENS: int = 1024
    SLIDING_WINDOW_MESSAGES: int = 20
    
    class Config:
        env_file = ".env"
        case_sensitive = True


settings = Settings()
