"""
Authentication Middleware - Extracts and validates JWT tokens.

Runs before route handlers to:
1. Extract JWT from Authorization header
2. Validate token signature and expiry
3. Check token blacklist
4. Attach user to request.state
"""
from typing import Callable
import logging

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.auth.jwt import verify_token
from app.auth.cache import AuthCache
from app.auth.dependencies import get_user_from_token
from app.database.models import AuthUser

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to authenticate requests via JWT tokens.
    
    Public endpoints (no auth required) should be excluded via
    PUBLIC_ENDPOINTS list or by not requiring authentication.
    """
    
    # Public endpoints that don't require authentication
    PUBLIC_ENDPOINTS = [
        "/api/v1/register",
        "/api/v1/login",
        "/api/v1/refresh",
        "/api/v1/forgot-password",
        "/api/v1/reset-password",
        "/api/v1/verify-email",
        "/api/v1/resend-verification",
        "/api/v1/health",
        "/docs",
        "/openapi.json",
        "/redoc",
    ]
    
    # Public path prefixes
    PUBLIC_PREFIXES = [
        "/webhooks/",  # Webhook endpoints
        "/api/v1/verify-email/",  # GET email verification
        "/api/v1/reset-password/",  # GET password reset form
    ]
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Process request and attach authenticated user."""
        
        # Skip authentication for public endpoints
        if self._is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        
        if not authorization:
            logger.debug(f"No Authorization header for {request.url.path}")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication required",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Parse Bearer token
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise ValueError("Invalid authorization scheme")
        except ValueError:
            logger.warning(f"Invalid Authorization header format: {authorization[:20]}...")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid authorization header format. Expected: Bearer <token>",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Verify token and get user
        try:
            # Verify token (checks signature, expiry, blacklist)
            payload = await verify_token(token)
            user_id = payload.get("sub")
            
            if not user_id:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid token payload"
                )
            
            # Get user from cache or database
            user = await get_user_from_token(user_id)
            
            if not user:
                logger.warning(f"User {user_id} not found")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="User not found"
                )
            
            # Attach user to request state
            request.state.user = user
            request.state.user_id = user.id
            
            logger.debug(f"Authenticated user {user.id} for {request.url.path}")
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Authentication error: {e}", exc_info=True)
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Authentication failed"
            )
        
        # Continue to next middleware/route handler
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
        
        return False
