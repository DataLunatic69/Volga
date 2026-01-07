"""
Rate Limiting Middleware - Enforces rate limits on API requests.

Uses Redis-based sliding window rate limiting with:
- Per-IP limits for unauthenticated requests
- Per-user limits for authenticated requests
- Different limits for auth endpoints vs general API
"""
import logging
from typing import Optional

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from app.core.rate_limit import (
    RateLimiter, 
    RateLimits, 
    get_rate_limit_for_path,
    RateLimitConfig
)

logger = logging.getLogger(__name__)


class RateLimitingMiddleware(BaseHTTPMiddleware):
    """
    Middleware to enforce rate limits on requests.
    
    Features:
    - IP-based limiting for unauthenticated requests
    - User-based limiting for authenticated requests
    - Endpoint-specific rate limits
    - Returns proper rate limit headers
    """
    
    # Paths to skip rate limiting
    SKIP_PATHS = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    }
    
    def __init__(self, app: ASGIApp, enabled: bool = True):
        """
        Initialize middleware.
        
        Args:
            app: ASGI application
            enabled: If False, skip rate limiting entirely
        """
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Check rate limit and process request."""
        
        # Skip if disabled
        if not self.enabled:
            return await call_next(request)
        
        # Skip certain paths
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)
        
        # Skip preflight requests
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Get client identifier (IP or user_id)
        identifier = self._get_identifier(request)
        is_authenticated = getattr(request.state, "authenticated", False)
        
        # Get rate limit config for this endpoint
        config = get_rate_limit_for_path(request.url.path, request.method)
        limit_type = self._get_limit_type(request.url.path)
        
        # Check rate limit
        allowed, remaining, reset_after = await RateLimiter.check_rate_limit(
            identifier=identifier,
            limit_type=limit_type,
            config=config,
            is_authenticated=is_authenticated
        )
        
        # Get rate limit headers
        headers = await RateLimiter.get_rate_limit_headers(config, remaining, reset_after)
        
        if not allowed:
            # Rate limit exceeded
            logger.warning(
                f"Rate limit exceeded: {identifier} on {request.url.path} "
                f"({config})"
            )
            return JSONResponse(
                status_code=429,
                content={
                    "detail": "Too many requests. Please try again later.",
                    "retry_after": reset_after
                },
                headers={
                    **headers,
                    "Retry-After": str(reset_after)
                }
            )
        
        # Continue to next middleware/route
        response = await call_next(request)
        
        # Add rate limit headers to response
        for header, value in headers.items():
            response.headers[header] = value
        
        return response
    
    def _get_identifier(self, request: Request) -> str:
        """Get unique identifier for rate limiting."""
        # Use user_id if authenticated
        user_id = getattr(request.state, "user_id", None)
        if user_id:
            return f"user:{user_id}"
        
        # Fall back to IP address
        # Check X-Forwarded-For for proxied requests
        forwarded_for = request.headers.get("X-Forwarded-For")
        if forwarded_for:
            # Get first IP in chain
            client_ip = forwarded_for.split(",")[0].strip()
        else:
            client_ip = request.client.host if request.client else "unknown"
        
        return f"ip:{client_ip}"
    
    def _get_limit_type(self, path: str) -> str:
        """Get limit type for logging/tracking."""
        if path.startswith("/api/v1/"):
            # Extract endpoint name
            parts = path.split("/")
            if len(parts) >= 4:
                return parts[3]  # e.g., "login", "register"
        return "api"

