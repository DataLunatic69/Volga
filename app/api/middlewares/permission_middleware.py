"""
Permission Middleware - Validates user permissions for routes.

This middleware works in conjunction with FastAPI dependencies.
It provides a centralized way to check permissions before routes execute.

Note: Most permission checks are done via dependencies (require_permission),
but this middleware can be used for route-level permission enforcement.
"""
from typing import Callable, Optional
import logging

from fastapi import Request, HTTPException, status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import Response

from app.auth.rbac import PermissionService
from app.auth.cache import permission_cache
from app.database.session import get_async_session_context

logger = logging.getLogger(__name__)


class PermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check permissions for routes.
    
    This is optional - most permission checks are done via dependencies.
    Use this middleware if you want route-level permission enforcement
    based on route metadata.
    """
    
    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """Check permissions if route requires them."""
        
        # Skip if no user authenticated (handled by AuthMiddleware)
        if not hasattr(request.state, "user") or not request.state.user:
            return await call_next(request)
        
        # Check if route has permission requirements in metadata
        route = request.scope.get("route")
        if route:
            required_permission = route.extra.get("required_permission")
            required_role = route.extra.get("required_role")
            
            if required_permission or required_role:
                user = request.state.user
                agency_id = self._extract_agency_id(request)
                
                if not agency_id:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail="Agency ID is required for permission checks"
                    )
                
                # Check permission or role
                async with get_async_session_context() as db:
                    permission_service = PermissionService(db)
                    
                    if required_permission:
                        has_permission = await permission_service.check_permission(
                            user.id,
                            agency_id,
                            required_permission
                        )
                        
                        if not has_permission:
                            logger.warning(
                                f"Permission denied: user {user.id} lacks '{required_permission}' "
                                f"for {request.url.path}"
                            )
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Permission denied: {required_permission}"
                            )
                    
                    if required_role:
                        has_role = await permission_service.has_role(
                            user.id,
                            agency_id,
                            required_role
                        )
                        
                        if not has_role:
                            logger.warning(
                                f"Role check failed: user {user.id} lacks role '{required_role}' "
                                f"for {request.url.path}"
                            )
                            raise HTTPException(
                                status_code=status.HTTP_403_FORBIDDEN,
                                detail=f"Role required: {required_role}"
                            )
        
        # Continue to route handler
        return await call_next(request)
    
    def _extract_agency_id(self, request: Request) -> Optional[str]:
        """Extract agency_id from request."""
        # Check path parameters
        agency_id = request.path_params.get("agency_id")
        if agency_id:
            return agency_id
        
        # Check query parameters
        agency_id = request.query_params.get("agency_id")
        if agency_id:
            return agency_id
        
        # Check request state (set by previous middleware/dependency)
        if hasattr(request.state, "agency_id"):
            return request.state.agency_id
        
        return None

