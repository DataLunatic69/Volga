"""
Application configuration module.
Loads environment variables and provides typed configuration settings.
"""
import os
from typing import Optional
from functools import lru_cache


class Settings:
    """Application settings loaded from environment variables."""
    
    # Application Settings
    APP_NAME: str = os.getenv("APP_NAME", "AI Receptionist Backend")
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    VERSION: str = os.getenv("VERSION", "0.1.0")
    
    # Server Settings
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))
    
    # Database Settings
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres:Aura%40123@db.qwddxnvcdkubctgkqtpa.supabase.co:5432/postgres"
    )
    DB_ECHO: bool = os.getenv("DB_ECHO", "False").lower() == "true"
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "15"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "10"))
    DB_POOL_PRE_PING: bool = os.getenv("DB_POOL_PRE_PING", "True").lower() == "true"
    
    # Redis Settings
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL", None)
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD", None)
    
    # LangSmith Settings (for LangChain/LangGraph observability)
    LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY", None)
    LANGSMITH_PROJECT: Optional[str] = os.getenv("LANGSMITH_PROJECT", None)
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "False").lower() == "true"
    
    # Groq API Settings (for LLM)
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY", None)
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    # OpenAI API Settings (alternative LLM provider)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY", None)
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # Qdrant Vector Database Settings
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL", None)
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY", None)
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "properties")
    
    # WhatsApp Business API Settings
    WHATSAPP_API_KEY: Optional[str] = os.getenv("WHATSAPP_API_KEY", None)
    WHATSAPP_API_SECRET: Optional[str] = os.getenv("WHATSAPP_API_SECRET", None)
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID", None)
    WHATSAPP_BUSINESS_ACCOUNT_ID: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ACCOUNT_ID", None)
    WHATSAPP_VERIFY_TOKEN: Optional[str] = os.getenv("WHATSAPP_VERIFY_TOKEN", None)
    WHATSAPP_WEBHOOK_SECRET: Optional[str] = os.getenv("WHATSAPP_WEBHOOK_SECRET", None)
    
    # Security Settings
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    
    # CORS Settings
    CORS_ORIGINS: list[str] = os.getenv(
        "CORS_ORIGINS", 
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    CORS_ALLOW_METHODS: list[str] = os.getenv(
        "CORS_ALLOW_METHODS",
        "GET,POST,PUT,DELETE,OPTIONS"
    ).split(",")
    CORS_ALLOW_HEADERS: list[str] = os.getenv(
        "CORS_ALLOW_HEADERS",
        "*"
    ).split(",")
    
    # Logging Settings
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text
    
    # Rate Limiting
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    
    # AI Agent Settings
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "3"))
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "30"))
    
    # Email Settings (for notifications)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST", None)
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER", None)
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD", None)
    SMTP_FROM_EMAIL: Optional[str] = os.getenv("SMTP_FROM_EMAIL", None)
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    
    # File Upload Settings
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB in bytes
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    
    @property
    def database_url(self) -> str:
        """Get the database URL."""
        return self.DATABASE_URL
    
    @property
    def redis_url(self) -> Optional[str]:
        """Get the Redis URL, constructing it if not provided directly."""
        if self.REDIS_URL:
            return self.REDIS_URL
        if self.REDIS_PASSWORD:
            return f"redis://:{self.REDIS_PASSWORD}@{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
        return f"redis://{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT.lower() == "production"
    
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT.lower() == "development"


@lru_cache()
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create a global settings instance
settings = get_settings()


