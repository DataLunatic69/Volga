"""
Authentication middleware for FastAPI.
Extracts and validates JWT tokens from requests.
"""
from typing import Optional
from uuid import UUID
from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.auth.jwt import decode_token
from app.auth.exceptions import InvalidTokenError, TokenExpiredError


class AuthMiddleware(BaseHTTPMiddleware):
    """
    Middleware to extract and validate JWT tokens from requests.
    Attaches user information to request state if token is valid.
    """
    
    def __init__(self, app, auto_error: bool = True):
        """
        Initialize auth middleware.
        
        Args:
            app: FastAPI application
            auto_error: If True, raise HTTPException on invalid token
        """
        super().__init__(app)
        self.auto_error = auto_error
    
    async def dispatch(self, request: Request, call_next):
        """
        Process request and extract token if present.
        
        Args:
            request: FastAPI request
            call_next: Next middleware/handler
            
        Returns:
            Response
        """
        # Skip authentication for certain paths
        if request.url.path in ["/", "/health", "/docs", "/openapi.json", "/redoc"]:
            return await call_next(request)
        
        # Extract token from Authorization header
        authorization = request.headers.get("Authorization")
        
        if authorization and authorization.startswith("Bearer "):
            token = authorization.split(" ")[1]
            
            try:
                # Decode token (without full verification - that happens in dependencies)
                # This is just to attach user info to request state
                payload = decode_token(token, verify=False)
                user_id = payload.get("sub")
                
                if user_id:
                    # Attach user_id to request state
                    try:
                        request.state.user_id = UUID(user_id)
                        request.state.user_email = payload.get("email")
                        request.state.token_payload = payload
                    except (ValueError, TypeError):
                        # Invalid UUID format, skip
                        pass
                
            except (InvalidTokenError, TokenExpiredError, ValueError):
                # Token invalid or expired, but don't raise error here
                # Let dependencies handle authentication errors
                if self.auto_error:
                    return Response(
                        content='{"detail":"Invalid token"}',
                        status_code=status.HTTP_401_UNAUTHORIZED,
                        media_type="application/json",
                        headers={"WWW-Authenticate": "Bearer"}
                    )
        
        return await call_next(request)
