"""
Application configuration module.
Loads environment variables and provides typed configuration settings.
"""
import os
from typing import Optional, List
from functools import lru_cache
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Settings:
    """Application settings loaded from environment variables."""
    
    # ====================
    # Application Settings
    # ====================
    APP_NAME: str = os.getenv("APP_NAME", "NexCell AI Receptionist")
    APP_VERSION: str = os.getenv("APP_VERSION", "2.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development").lower()
    DEBUG: bool = os.getenv("DEBUG", "true").lower() == "true"
    
    # ====================
    # Server Settings
    # ====================
    API_HOST: str = os.getenv("API_HOST", "0.0.0.0")
    API_PORT: int = int(os.getenv("API_PORT", "8000"))
    
    # Backend Domain (for email links)
    BACKEND_DOMAIN: str = os.getenv(
        "BACKEND_DOMAIN",
        f"http://localhost:{os.getenv('API_PORT', '8000')}"
    )
    
    # ====================
    # Database Settings (Supabase)
    # ====================
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+asyncpg://postgres.qwddxnvcdkubctgkqtpa:Aura%40123@aws-1-ap-south-1.pooler.supabase.com:5432/postgres"
    )
    SUPABASE_URL: Optional[str] = os.getenv("SUPABASE_URL")
    SUPABASE_KEY: Optional[str] = os.getenv("SUPABASE_KEY")
    
    # Database Connection Pool Settings
    DB_POOL_SIZE: int = int(os.getenv("DB_POOL_SIZE", "10"))
    DB_MAX_OVERFLOW: int = int(os.getenv("DB_MAX_OVERFLOW", "20"))
    DB_POOL_PRE_PING: bool = os.getenv("DB_POOL_PRE_PING", "True").lower() == "true"
    DB_POOL_RECYCLE: int = int(os.getenv("DB_POOL_RECYCLE", "3600"))  # 1 hour
    
    # ====================
    # Redis Settings
    # ====================
    REDIS_URL: Optional[str] = os.getenv("REDIS_URL")
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: Optional[str] = os.getenv("REDIS_PASSWORD")
    REDIS_SSL: bool = os.getenv("REDIS_SSL", "False").lower() == "true"
    
    # ====================
    # AI/LLM Settings
    # ====================
    GROQ_API_KEY: Optional[str] = os.getenv("GROQ_API_KEY")
    GROQ_MODEL: str = os.getenv("GROQ_MODEL", "mixtral-8x7b-32768")
    
    # OpenAI (alternative)
    OPENAI_API_KEY: Optional[str] = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL: str = os.getenv("OPENAI_MODEL", "gpt-4")
    
    # LangSmith (Observability)
    LANGSMITH_API_KEY: Optional[str] = os.getenv("LANGSMITH_API_KEY")
    LANGSMITH_PROJECT: Optional[str] = os.getenv("LANGSMITH_PROJECT")
    LANGSMITH_TRACING: bool = os.getenv("LANGSMITH_TRACING", "False").lower() == "true"
    
    
    # ====================
    # Vector Database (Qdrant)
    # ====================
    QDRANT_URL: Optional[str] = os.getenv("QDRANT_URL")
    QDRANT_API_KEY: Optional[str] = os.getenv("QDRANT_API_KEY")
    QDRANT_COLLECTION_NAME: str = os.getenv("QDRANT_COLLECTION_NAME", "properties")
    
    def __post_init__(self):
        """Validate settings after initialization."""
        # Validate Qdrant settings if URL is provided
        if self.QDRANT_URL and not self.QDRANT_API_KEY:
            raise ValueError("QDRANT_API_KEY must be set when QDRANT_URL is provided")
    
    # ====================
    # WhatsApp Business API
    # ====================
    WHATSAPP_BUSINESS_ID: Optional[str] = os.getenv("WHATSAPP_BUSINESS_ID")
    WHATSAPP_ACCESS_TOKEN: Optional[str] = os.getenv("WHATSAPP_ACCESS_TOKEN")
    WHATSAPP_WEBHOOK_SECRET: Optional[str] = os.getenv("WHATSAPP_WEBHOOK_SECRET")
    WHATSAPP_PHONE_NUMBER_ID: Optional[str] = os.getenv("WHATSAPP_PHONE_NUMBER_ID")
    WHATSAPP_VERIFY_TOKEN: Optional[str] = os.getenv("WHATSAPP_VERIFY_TOKEN")
    
    # ====================
    # Security & JWT
    # ====================
    JWT_SECRET_KEY: str = os.getenv("JWT_SECRET_KEY", "your-256-bit-secret-key-change-in-production")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    JWT_ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("JWT_ACCESS_TOKEN_EXPIRE_MINUTES", "30"))
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = int(os.getenv("JWT_REFRESH_TOKEN_EXPIRE_DAYS", "30"))
    ENCRYPTION_KEY: Optional[str] = os.getenv("ENCRYPTION_KEY")  # For encrypting sensitive data
    
    # ====================
    # Authentication Settings
    # ====================
    AUTH_MAX_FAILED_ATTEMPTS: int = int(os.getenv("AUTH_MAX_FAILED_ATTEMPTS", "5"))
    AUTH_LOCKOUT_DURATION_MINUTES: int = int(os.getenv("AUTH_LOCKOUT_DURATION_MINUTES", "30"))
    AUTH_EMAIL_VERIFICATION_EXPIRE_HOURS: int = int(os.getenv("AUTH_EMAIL_VERIFICATION_EXPIRE_HOURS", "24"))
    AUTH_PASSWORD_RESET_EXPIRE_HOURS: int = int(os.getenv("AUTH_PASSWORD_RESET_EXPIRE_HOURS", "1"))
    
    # ====================
    # CORS Settings
    # ====================
    CORS_ORIGINS: List[str] = os.getenv(
        "CORS_ORIGINS",
        "http://localhost:3000,http://localhost:8000"
    ).split(",")
    CORS_ALLOW_CREDENTIALS: bool = os.getenv("CORS_ALLOW_CREDENTIALS", "True").lower() == "true"
    CORS_ALLOW_METHODS: List[str] = os.getenv(
        "CORS_ALLOW_METHODS",
        "GET,POST,PUT,DELETE,OPTIONS,PATCH"
    ).split(",")
    CORS_ALLOW_HEADERS: List[str] = os.getenv(
        "CORS_ALLOW_HEADERS",
        "Content-Type,Authorization,X-Requested-With,X-API-Key"
    ).split(",")
    
    # ====================
    # Email Settings (SMTP)
    # ====================
    MAIL_SERVER: Optional[str] = os.getenv("MAIL_SERVER")
    MAIL_PORT: int = int(os.getenv("MAIL_PORT", "587"))
    MAIL_USERNAME: Optional[str] = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD: Optional[str] = os.getenv("MAIL_PASSWORD")
    MAIL_FROM: Optional[str] = os.getenv("MAIL_FROM")
    MAIL_FROM_NAME: Optional[str] = os.getenv("MAIL_FROM_NAME", "NexCell AI Receptionist")
    MAIL_STARTTLS: bool = os.getenv("MAIL_STARTTLS", "True").lower() == "true"
    MAIL_SSL_TLS: bool = os.getenv("MAIL_SSL_TLS", "False").lower() == "true"
    
    # Legacy support (deprecated - use MAIL_* variables instead)
    SMTP_HOST: Optional[str] = os.getenv("SMTP_HOST") or os.getenv("MAIL_SERVER")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT") or os.getenv("MAIL_PORT", "587"))
    SMTP_USER: Optional[str] = os.getenv("SMTP_USER") or os.getenv("MAIL_USERNAME")
    SMTP_PASSWORD: Optional[str] = os.getenv("SMTP_PASSWORD") or os.getenv("MAIL_PASSWORD")
    EMAIL_FROM: Optional[str] = os.getenv("EMAIL_FROM") or os.getenv("MAIL_FROM")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "True").lower() == "true"
    
    # ====================
    # Logging Settings
    # ====================
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO").upper()
    LOG_FORMAT: str = os.getenv("LOG_FORMAT", "json")  # json or text
    LOG_FILE: Optional[str] = os.getenv("LOG_FILE")
    
    # ====================
    # Rate Limiting
    # ====================
    RATE_LIMIT_ENABLED: bool = os.getenv("RATE_LIMIT_ENABLED", "True").lower() == "true"
    RATE_LIMIT_PER_MINUTE: int = int(os.getenv("RATE_LIMIT_PER_MINUTE", "60"))
    RATE_LIMIT_PER_HOUR: int = int(os.getenv("RATE_LIMIT_PER_HOUR", "1000"))
    
    # ====================
    # AI Agent Settings
    # ====================
    AI_CONFIDENCE_THRESHOLD: float = float(os.getenv("AI_CONFIDENCE_THRESHOLD", "0.7"))
    AI_MAX_RETRIES: int = int(os.getenv("AI_MAX_RETRIES", "3"))
    AI_TIMEOUT_SECONDS: int = int(os.getenv("AI_TIMEOUT_SECONDS", "30"))
    AI_TEMPERATURE: float = float(os.getenv("AI_TEMPERATURE", "0.1"))
    
    # ====================
    # File Upload Settings
    # ====================
    MAX_UPLOAD_SIZE: int = int(os.getenv("MAX_UPLOAD_SIZE", "10485760"))  # 10MB in bytes
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    ALLOWED_EXTENSIONS: List[str] = os.getenv(
        "ALLOWED_EXTENSIONS",
        "jpg,jpeg,png,pdf,doc,docx,txt"
    ).split(",")
    
    # ====================
    # WhatsApp Flow Settings
    # ====================
    WHATSAPP_SESSION_TIMEOUT_MINUTES: int = int(os.getenv("WHATSAPP_SESSION_TIMEOUT_MINUTES", "60"))
    WHATSAPP_MAX_MESSAGE_LENGTH: int = int(os.getenv("WHATSAPP_MAX_MESSAGE_LENGTH", "4096"))
    WHATSAPP_RETRY_ATTEMPTS: int = int(os.getenv("WHATSAPP_RETRY_ATTEMPTS", "3"))
    
    # ====================
    # Business Logic Settings
    # ====================
    VIEWING_DURATION_MINUTES: int = int(os.getenv("VIEWING_DURATION_MINUTES", "30"))
    VIEWING_REMINDER_HOURS: int = int(os.getenv("VIEWING_REMINDER_HOURS", "24"))
    LEAD_SCORE_THRESHOLD: int = int(os.getenv("LEAD_SCORE_THRESHOLD", "70"))
    
    # ====================
    # Properties
    # ====================
    
    @property
    def is_production(self) -> bool:
        """Check if running in production environment."""
        return self.ENVIRONMENT == "production"
    
    @property
    def is_development(self) -> bool:
        """Check if running in development environment."""
        return self.ENVIRONMENT == "development"
    
    @property
    def is_testing(self) -> bool:
        """Check if running in testing environment."""
        return self.ENVIRONMENT == "testing"
    
    @property
    def sync_database_url(self) -> str:
        """Get synchronous database URL for migrations."""
        return self.DATABASE_URL.replace("+asyncpg", "")
    
    @property
    def alembic_database_url(self) -> str:
        """Get database URL for Alembic migrations."""
        return self.sync_database_url
    
    @property
    def redis_connection_url(self) -> Optional[str]:
        """Get the Redis URL, constructing it if not provided directly."""
        if self.REDIS_URL:
            # If REDIS_URL is provided, ensure it has protocol
            if not self.REDIS_URL.startswith(("redis://", "rediss://")):
                # If it's just host:port, add protocol
                if "://" not in self.REDIS_URL:
                    protocol = "rediss://" if self.REDIS_SSL else "redis://"
                    # Handle format: host:port or host:port/db
                    if "/" in self.REDIS_URL:
                        return f"{protocol}{self.REDIS_URL}"
                    else:
                        return f"{protocol}{self.REDIS_URL}/{self.REDIS_DB}"
            return self.REDIS_URL
        
        auth_part = ""
        if self.REDIS_PASSWORD:
            auth_part = f":{self.REDIS_PASSWORD}@"
        
        protocol = "rediss://" if self.REDIS_SSL else "redis://"
        
        return f"{protocol}{auth_part}{self.REDIS_HOST}:{self.REDIS_PORT}/{self.REDIS_DB}"
    
    @property
    def smtp_connection(self) -> dict:
        """Get SMTP connection configuration."""
        return {
            "host": self.MAIL_SERVER or self.SMTP_HOST,
            "port": self.MAIL_PORT,
            "username": self.MAIL_USERNAME or self.SMTP_USER,
            "password": self.MAIL_PASSWORD or self.SMTP_PASSWORD,
            "use_tls": self.MAIL_STARTTLS or self.SMTP_USE_TLS,
            "from_email": self.MAIL_FROM or self.EMAIL_FROM,
            "from_name": self.MAIL_FROM_NAME
        }
    
    @property
    def whatsapp_config(self) -> dict:
        """Get WhatsApp Business API configuration."""
        return {
            "business_id": self.WHATSAPP_BUSINESS_ID,
            "access_token": self.WHATSAPP_ACCESS_TOKEN,
            "phone_number_id": self.WHATSAPP_PHONE_NUMBER_ID,
            "webhook_secret": self.WHATSAPP_WEBHOOK_SECRET,
            "verify_token": self.WHATSAPP_VERIFY_TOKEN
        }
    
    @property
    def qdrant_config(self) -> dict:
        """Get Qdrant vector database configuration."""
        return {
            "url": self.QDRANT_URL,
            "api_key": self.QDRANT_API_KEY,
            "collection_name": self.QDRANT_COLLECTION_NAME
        }
    
    @property
    def ai_config(self) -> dict:
        """Get AI/LLM configuration."""
        return {
            "groq_api_key": self.GROQ_API_KEY,
            "groq_model": self.GROQ_MODEL,
            "openai_api_key": self.OPENAI_API_KEY,
            "openai_model": self.OPENAI_MODEL,
            "temperature": self.AI_TEMPERATURE,
            "max_retries": self.AI_MAX_RETRIES,
            "timeout": self.AI_TIMEOUT_SECONDS
        }


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Get cached settings instance."""
    return Settings()


# Create a global settings instance
settings = get_settings()