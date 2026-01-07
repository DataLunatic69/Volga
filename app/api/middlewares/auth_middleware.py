"""
Authentication Middleware - Extracts and validates JWT tokens.

Runs before route handlers to:
1. Extract JWT from Authorization header
2. Validate token signature and expiry
3. Check token blacklist (cached)
4. Attach user to request.state (from cache or DB)

NOTE: Uses Response objects instead of HTTPException for proper middleware error handling.
"""
from typing import Optional, Set
import logging
import time

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from app.auth.jwt import decode_token
from app.auth.cache import AuthCache
from app.auth.exceptions import InvalidTokenError, TokenExpiredError

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to authenticate requests via JWT tokens.
    
    Key Features:
    - Skips public endpoints (no auth required)
    - Validates JWT tokens synchronously (decode only)
    - Checks token blacklist via Redis cache
    - Attaches user info to request.state from cache
    - Returns JSONResponse on errors (not HTTPException)
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS: Set[str] = {
        "/",
        "/health",
        "/docs",
        "/openapi.json",
        "/redoc",
        "/api/v1/register",
        "/api/v1/login",
        "/api/v1/refresh",
        "/api/v1/forgot-password",
        "/api/v1/resend-verification",
    }
    
    # Public path prefixes (for dynamic paths)
    PUBLIC_PREFIXES = (
        "/webhooks/",
        "/api/v1/verify-email/",  # GET email verification
        "/api/v1/reset-password/",  # GET password reset form
        "/static/",
    )
    
    def __init__(self, app: ASGIApp, auto_error: bool = True):
        """
        Initialize middleware.
        
        Args:
            app: ASGI application
            auto_error: If True, return 401 for missing/invalid tokens.
                       If False, continue without user (for optional auth).
        """
        super().__init__(app)
        self.auto_error = auto_error
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Process request and attach authenticated user."""
        start_time = time.time()
        
        # Initialize request state
        request.state.user = None
        request.state.user_id = None
        request.state.authenticated = False
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            response = await call_next(request)
            return response
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization", "")
        
        if not authorization:
            if self.auto_error:
                return self._error_response(
                    401, "Authentication required", 
                    {"WWW-Authenticate": "Bearer"}
                )
            return await call_next(request)
        
        # Parse Bearer token
        parts = authorization.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            if self.auto_error:
                return self._error_response(
                    401, "Invalid authorization header. Expected: Bearer <token>",
                    {"WWW-Authenticate": "Bearer"}
                )
            return await call_next(request)
        
        token = parts[1]
        
        # Verify token
        try:
            # Decode token (synchronous - just signature/expiry check)
            payload = decode_token(token)
            user_id = payload.get("sub")
            jti = payload.get("jti")
            
            if not user_id:
                if self.auto_error:
                    return self._error_response(401, "Invalid token: missing user ID")
                return await call_next(request)
            
            # Check token blacklist (async Redis call)
            if jti and await AuthCache.is_token_blacklisted(jti):
                logger.warning(f"Blacklisted token used: {jti[:8]}...")
                if self.auto_error:
                    return self._error_response(401, "Token has been revoked")
                return await call_next(request)
            
            # Get user from cache (fast path)
            cached_user = await AuthCache.get_user(user_id)
            
            if cached_user:
                # User found in cache - attach to request
                request.state.user = cached_user
                request.state.user_id = user_id
                request.state.authenticated = True
                request.state.from_cache = True
            else:
                # User not in cache - will be fetched by dependency if needed
                # Just attach user_id for now
                request.state.user_id = user_id
                request.state.authenticated = True
                request.state.from_cache = False
            
            # Log successful auth
            duration_ms = (time.time() - start_time) * 1000
            logger.debug(
                f"Auth success: user={user_id[:8]}... path={request.url.path} "
                f"duration={duration_ms:.1f}ms cache={'hit' if cached_user else 'miss'}"
            )
            
        except TokenExpiredError:
            logger.debug(f"Expired token for {request.url.path}")
            if self.auto_error:
                return self._error_response(401, "Token has expired")
            return await call_next(request)
            
        except InvalidTokenError as e:
            logger.warning(f"Invalid token: {e}")
            if self.auto_error:
                return self._error_response(401, f"Invalid token: {e}")
            return await call_next(request)
            
        except Exception as e:
            logger.error(f"Auth middleware error: {e}", exc_info=True)
            if self.auto_error:
                return self._error_response(401, "Authentication failed")
            return await call_next(request)
        
        # Continue to next middleware/route
        response = await call_next(request)
        return response
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint is public (no auth required)."""
        # Check exact matches
        if path in self.PUBLIC_ENDPOINTS:
            return True
        
        # Check prefixes
        for prefix in self.PUBLIC_PREFIXES:
            if path.startswith(prefix):
                return True
        
        # Check POST endpoints for reset-password and verify-email
        if path == "/api/v1/reset-password" or path == "/api/v1/verify-email":
            return True
        
        return False
    
    def _error_response(
        self, 
        status_code: int, 
        detail: str, 
        headers: Optional[dict] = None
    ) -> JSONResponse:
        """Create error response (not exception)."""
        return JSONResponse(
            status_code=status_code,
            content={"detail": detail},
            headers=headers
        )
