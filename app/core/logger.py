"""
Structured logging configuration for the application.
Provides JSON and text formatters with context enrichment.
"""
import logging
import sys
from typing import Any, Dict, Optional
from datetime import datetime
import json
from pathlib import Path

from app.config import settings


class JSONFormatter(logging.Formatter):
    """Custom JSON formatter for structured logging."""
    
    def format(self, record: logging.LogRecord) -> str:
        """Format log record as JSON.
        
        Args:
            record: Log record to format
            
        Returns:
            JSON formatted log string
        """
        log_data: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno,
        }
        
        # Add exception info if present
        if record.exc_info:
            log_data["exception"] = self.formatException(record.exc_info)
        
        # Add extra fields from record
        if hasattr(record, "user_id"):
            log_data["user_id"] = record.user_id
        
        if hasattr(record, "agency_id"):
            log_data["agency_id"] = record.agency_id
        
        if hasattr(record, "conversation_id"):
            log_data["conversation_id"] = record.conversation_id
        
        if hasattr(record, "request_id"):
            log_data["request_id"] = record.request_id
        
        if hasattr(record, "duration_ms"):
            log_data["duration_ms"] = record.duration_ms
        
        if hasattr(record, "status_code"):
            log_data["status_code"] = record.status_code
        
        # Add custom extra fields
        if hasattr(record, "extra"):
            log_data["extra"] = record.extra
        
        return json.dumps(log_data)


class TextFormatter(logging.Formatter):
    """Custom text formatter for human-readable logs."""
    
    def __init__(self):
        super().__init__(
            fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S"
        )


def setup_logging() -> None:
    """Configure logging for the application."""
    
    # Get root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(settings.LOG_LEVEL)
    
    # Remove existing handlers
    root_logger.handlers.clear()
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(settings.LOG_LEVEL)
    
    # Choose formatter based on config
    if settings.LOG_FORMAT == "json":
        formatter = JSONFormatter()
    else:
        formatter = TextFormatter()
    
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # File handler (if configured)
    if settings.LOG_FILE:
        log_file_path = Path(settings.LOG_FILE)
        log_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(settings.LOG_FILE)
        file_handler.setLevel(settings.LOG_LEVEL)
        file_handler.setFormatter(formatter)
        root_logger.addHandler(file_handler)
    
    # Set log levels for third-party libraries
    logging.getLogger("uvicorn").setLevel(logging.INFO)
    logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
    
    # Log startup message
    root_logger.info(
        f"Logging configured: level={settings.LOG_LEVEL}, format={settings.LOG_FORMAT}"
    )


def get_logger(name: str) -> logging.Logger:
    """Get a logger instance with the given name.
    
    Args:
        name: Name for the logger (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)


class LoggerAdapter(logging.LoggerAdapter):
    """Custom logger adapter to add contextual information to logs."""
    
    def __init__(
        self,
        logger: logging.Logger,
        extra: Optional[Dict[str, Any]] = None
    ):
        """Initialize the adapter.
        
        Args:
            logger: Base logger instance
            extra: Extra context to add to all log messages
        """
        super().__init__(logger, extra or {})
    
    def process(
        self,
        msg: str,
        kwargs: Dict[str, Any]
    ) -> tuple[str, Dict[str, Any]]:
        """Process log message and add context.
        
        Args:
            msg: Log message
            kwargs: Keyword arguments
            
        Returns:
            Processed message and kwargs
        """
        # Merge extra context
        if "extra" not in kwargs:
            kwargs["extra"] = {}
        
        kwargs["extra"].update(self.extra)
        
        return msg, kwargs


def get_contextual_logger(
    name: str,
    user_id: Optional[str] = None,
    agency_id: Optional[str] = None,
    conversation_id: Optional[str] = None,
    request_id: Optional[str] = None,
    **kwargs
) -> LoggerAdapter:
    """Get a logger with contextual information.
    
    Args:
        name: Logger name
        user_id: User ID for context
        agency_id: Agency ID for context
        conversation_id: Conversation ID for context
        request_id: Request ID for context
        **kwargs: Additional context
        
    Returns:
        Logger adapter with context
    """
    logger = get_logger(name)
    
    context = {}
    
    if user_id:
        context["user_id"] = user_id
    
    if agency_id:
        context["agency_id"] = agency_id
    
    if conversation_id:
        context["conversation_id"] = conversation_id
    
    if request_id:
        context["request_id"] = request_id
    
    context.update(kwargs)
    
    return LoggerAdapter(logger, extra=context)


# Initialize logging on module import
setup_logging()


