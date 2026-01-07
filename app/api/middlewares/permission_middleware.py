"""
Permission Middleware - Validates user permissions for routes.

NOTE: Most permission checks are done via FastAPI dependencies (require_permission).
This middleware provides an additional layer for route-level enforcement.

It checks:
1. Route metadata for required permissions/roles
2. User has required access in agency context
"""
import logging
from typing import Optional
from uuid import UUID

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from starlette.types import ASGIApp

from app.auth.rbac import PermissionService
from app.auth.cache import permission_cache
from app.database.session import get_async_session_context

logger = logging.getLogger(__name__)


class PermissionMiddleware(BaseHTTPMiddleware):
    """
    Middleware to check permissions for routes.
    
    This is OPTIONAL - most permission checks are done via dependencies.
    Use this for additional route-level enforcement.
    """
    
    def __init__(self, app: ASGIApp, enabled: bool = True):
        """
        Initialize middleware.
        
        Args:
            app: ASGI application
            enabled: If False, skip permission checks entirely
        """
        super().__init__(app)
        self.enabled = enabled
    
    async def dispatch(self, request: Request, call_next) -> Response:
        """Check permissions if route requires them."""
        
        if not self.enabled:
            return await call_next(request)
        
        # Skip if no user authenticated
        if not getattr(request.state, "authenticated", False):
            return await call_next(request)
        
        # Get route from scope
        route = request.scope.get("route")
        if not route:
            return await call_next(request)
        
        # Check for permission requirements in endpoint
        endpoint = request.scope.get("endpoint")
        if not endpoint:
            return await call_next(request)
        
        # Check for permission attributes on endpoint function
        required_permissions = getattr(endpoint, "required_permissions", None)
        required_roles = getattr(endpoint, "required_roles", None)
        
        if not required_permissions and not required_roles:
            return await call_next(request)
        
        # Get user and agency context
        user_id = getattr(request.state, "user_id", None)
        if not user_id:
            return await call_next(request)
        
        agency_id = self._extract_agency_id(request)
        if not agency_id:
            return JSONResponse(
                status_code=400,
                content={"detail": "Agency ID is required for this operation"}
            )
        
        # Check permissions
        try:
            # Try cache first for permissions
            if required_permissions:
                cached_perms = await permission_cache.get_user_permissions(user_id, agency_id)
                
                if cached_perms is not None:
                    # Check from cache
                    missing = [p for p in required_permissions if p not in cached_perms]
                    if missing:
                        logger.warning(
                            f"Permission denied: user {user_id} lacks {missing} "
                            f"for {request.url.path}"
                        )
                        return JSONResponse(
                            status_code=403,
                            content={"detail": f"Missing permissions: {', '.join(missing)}"}
                        )
                else:
                    # Cache miss - check via database
                    async with get_async_session_context() as db:
                        permission_service = PermissionService(db)
                        
                        for perm in required_permissions:
                            has_perm = await permission_service.check_permission(
                                user_id, agency_id, perm
                            )
                            if not has_perm:
                                logger.warning(
                                    f"Permission denied: user {user_id} lacks '{perm}' "
                                    f"for {request.url.path}"
                                )
                                return JSONResponse(
                                    status_code=403,
                                    content={"detail": f"Permission denied: {perm}"}
                                )
            
            # Check roles
            if required_roles:
                async with get_async_session_context() as db:
                    permission_service = PermissionService(db)
                    
                    has_any_role = False
                    for role in required_roles:
                        if await permission_service.has_role(user_id, agency_id, role):
                            has_any_role = True
                            break
                    
                    if not has_any_role:
                        logger.warning(
                            f"Role check failed: user {user_id} lacks any of {required_roles} "
                            f"for {request.url.path}"
                        )
                        return JSONResponse(
                            status_code=403,
                            content={"detail": f"Required role: {' or '.join(required_roles)}"}
                        )
                        
        except Exception as e:
            logger.error(f"Permission middleware error: {e}", exc_info=True)
            return JSONResponse(
                status_code=500,
                content={"detail": "Permission check failed"}
            )
        
        # All checks passed
        return await call_next(request)
    
    def _extract_agency_id(self, request: Request) -> Optional[UUID]:
        """Extract agency_id from request."""
        # Check path parameters
        agency_id_str = request.path_params.get("agency_id")
        if agency_id_str:
            try:
                return UUID(agency_id_str)
            except ValueError:
                pass
        
        # Check query parameters
        agency_id_str = request.query_params.get("agency_id")
        if agency_id_str:
            try:
                return UUID(agency_id_str)
            except ValueError:
                pass
        
        # Check request state
        if hasattr(request.state, "agency_id"):
            return request.state.agency_id
        
        return None
