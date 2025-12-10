"""Application configuration and environment variables."""
import os
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""
    
    # Application
    APP_NAME: str = "NexCell AI Receptionist"
    APP_VERSION: str = "0.1.0"
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    
    # API
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # WhatsApp
    WHATSAPP_PHONE_ID: str = os.getenv("WHATSAPP_PHONE_ID", "")
    WHATSAPP_BUSINESS_ACCOUNT_ID: str = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", "")
    WHATSAPP_ACCESS_TOKEN: str = os.getenv("WHATSAPP_ACCESS_TOKEN", "")
    WHATSAPP_WEBHOOK_VERIFY_TOKEN: str = os.getenv("WHATSAPP_WEBHOOK_VERIFY_TOKEN", "")
    
    # Database
    DATABASE_URL: str = os.getenv("DATABASE_URL", "postgresql://user:password@localhost/nexcell")
    
    # Redis
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Vector DB
    QDRANT_URL: str = os.getenv("QDRANT_URL", "")
    QDRANT_API_KEY:  str = os.getenv("QDRANT_API_KEY", "")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "properties")
    
    # LLM
    GROQ_API_KEY: str = os.getenv("GROQ_API_KEY", "")
    LLM_MODEL: str = os.getenv("LLM_MODEL", "qwen/qwen3-32b")
    
    class Config:
        """Pydantic configuration."""
        env_file = ".env"


settings = Settings()
