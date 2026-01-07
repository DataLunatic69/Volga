"""
Request Logging Middleware - Logs all HTTP requests with context.

Features:
- Request ID generation and tracking
- Request/response timing
- Structured logging with user context
- Error tracking
"""
import time
import uuid
import logging
from typing import Callable

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response
from starlette.types import ASGIApp

logger = logging.getLogger(__name__)


class LoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log HTTP requests with context.
    
    Adds:
    - Request ID to all requests
    - Request timing
    - User context (if authenticated)
    - Response status logging
    """
    
    # Paths to skip detailed logging (reduce noise)
    SKIP_DETAILED_PATHS = {
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    def __init__(self, app: ASGIApp, log_request_body: bool = False):
        """
        Initialize middleware.
        
        Args:
            app: ASGI application
            log_request_body: If True, log request bodies (use with caution)
        """
        super().__init__(app)
        self.log_request_body = log_request_body
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log request and response."""
        
        # Generate request ID
        request_id = str(uuid.uuid4())[:8]
        request.state.request_id = request_id
        
        # Get client IP
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        # Start timing
        start_time = time.time()
        
        # Skip detailed logging for noisy endpoints
        detailed_logging = request.url.path not in self.SKIP_DETAILED_PATHS
        
        # Log request
        if detailed_logging:
            user_id = getattr(request.state, "user_id", None)
            logger.info(
                f"[{request_id}] --> {request.method} {request.url.path} "
                f"client={client_ip} user={user_id or 'anonymous'}"
            )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Add request ID to response headers
            response.headers["X-Request-ID"] = request_id
            
            # Log response
            if detailed_logging:
                log_level = logging.INFO if response.status_code < 400 else logging.WARNING
                logger.log(
                    log_level,
                    f"[{request_id}] <-- {response.status_code} "
                    f"duration={duration_ms:.1f}ms"
                )
            
            return response
            
        except Exception as e:
            # Log exception
            duration_ms = (time.time() - start_time) * 1000
            logger.error(
                f"[{request_id}] <-- ERROR {type(e).__name__}: {e} "
                f"duration={duration_ms:.1f}ms",
                exc_info=True
            )
            raise


class SecurityLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to log security-related events.
    
    Logs:
    - Authentication failures
    - Permission denials
    - Rate limit violations
    - Suspicious activity
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Log security events."""
        
        response = await call_next(request)
        
        # Log security events based on response status
        if response.status_code == 401:
            self._log_auth_failure(request)
        elif response.status_code == 403:
            self._log_permission_denied(request)
        elif response.status_code == 429:
            self._log_rate_limit(request)
        
        return response
    
    def _log_auth_failure(self, request: Request) -> None:
        """Log authentication failure."""
        client_ip = self._get_client_ip(request)
        logger.warning(
            f"AUTH_FAILURE: {request.method} {request.url.path} "
            f"client={client_ip}"
        )
    
    def _log_permission_denied(self, request: Request) -> None:
        """Log permission denial."""
        user_id = getattr(request.state, "user_id", None)
        logger.warning(
            f"PERMISSION_DENIED: {request.method} {request.url.path} "
            f"user={user_id or 'anonymous'}"
        )
    
    def _log_rate_limit(self, request: Request) -> None:
        """Log rate limit violation."""
        client_ip = self._get_client_ip(request)
        user_id = getattr(request.state, "user_id", None)
        logger.warning(
            f"RATE_LIMIT: {request.method} {request.url.path} "
            f"client={client_ip} user={user_id or 'anonymous'}"
        )
    
    def _get_client_ip(self, request: Request) -> str:
        """Get client IP from request."""
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            return forwarded_for.split(",")[0].strip()
        return request.client.host if request.client else "unknown"

