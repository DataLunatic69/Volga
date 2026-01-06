"""
Permission Dependencies - FastAPI dependencies and decorators for RBAC.

Usage in endpoints:
    @router.get("/contacts")
    async def get_contacts(
        current_user: AuthUser = Depends(get_current_user),
        _: None = Depends(require_permission("contacts.view"))
    ):
        ...

Or use the decorator:
    @require_permission("contacts.edit")
    @router.put("/contacts/{contact_id}")
    async def update_contact(...):
        ...
"""
from functools import wraps
from typing import Callable, Optional
from uuid import UUID

from fastapi import Depends, Request, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import AuthUser
from app.services.permission_service import PermissionService
from app.auth.permission_cache import permission_cache
from app.auth.exceptions import PermissionDeniedError
from app.auth.dependencies import get_current_user
import logging

logger = logging.getLogger(__name__)


# ============================================================
# Helper Functions
# ============================================================

async def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    """Dependency to get PermissionService instance."""
    return PermissionService(db)


async def get_user_permissions_cached(
    user_id: UUID,
    agency_id: UUID,
    permission_service: PermissionService
) -> set[str]:
    """
    Get user permissions with caching.
    
    Checks cache first, falls back to database.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_service: PermissionService instance
        
    Returns:
        Set of permission names
    """
    # Try cache first
    cached_permissions = await permission_cache.get_user_permissions(user_id, agency_id)
    
    if cached_permissions is not None:
        logger.debug(f"Cache hit: permissions for user {user_id} in agency {agency_id}")
        return cached_permissions
    
    # Cache miss - load from database
    logger.debug(f"Cache miss: loading permissions for user {user_id}")
    permissions = await permission_service.get_user_permissions(user_id, agency_id)
    
    # Cache for future requests
    await permission_cache.set_user_permissions(user_id, agency_id, permissions)
    
    return permissions


async def extract_agency_id_from_request(request: Request) -> Optional[UUID]:
    """
    Extract agency_id from request.
    
    Looks in (in order):
    1. Path parameters (e.g., /agencies/{agency_id}/...)
    2. Query parameters (?agency_id=...)
    3. Request body (JSON)
    4. User's state (if user has default agency)
    
    Args:
        request: FastAPI Request object
        
    Returns:
        UUID of agency or None
    """
    # Check path parameters
    agency_id = request.path_params.get("agency_id")
    if agency_id:
        try:
            return UUID(agency_id)
        except ValueError:
            pass
    
    # Check query parameters
    agency_id = request.query_params.get("agency_id")
    if agency_id:
        try:
            return UUID(agency_id)
        except ValueError:
            pass
    
    # Check request state (set by middleware or previous dependencies)
    if hasattr(request.state, "agency_id"):
        return request.state.agency_id
    
    # Check body (only for POST/PUT/PATCH)
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
            agency_id = body.get("agency_id")
            if agency_id:
                return UUID(agency_id)
        except Exception:
            pass
    
    return None


# ============================================================
# Permission Check Dependencies
# ============================================================

def require_permission(permission_name: str):
    """
    Dependency factory to require specific permission.
    
    Usage:
        @router.get("/contacts")
        async def get_contacts(
            current_user: AuthUser = Depends(get_current_user),
            _: None = Depends(require_permission("contacts.view"))
        ):
            ...
    
    Args:
        permission_name: Permission name (e.g., "contacts.view")
        
    Returns:
        FastAPI dependency function
    """
    async def check_permission(
        request: Request,
        current_user: AuthUser = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        """Check if current user has required permission."""
        # Extract agency_id from request
        agency_id = await extract_agency_id_from_request(request)
        
        if not agency_id:
            logger.warning(
                f"Permission check failed: no agency_id found for user {current_user.id}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency ID is required for this operation"
            )
        
        # Get user permissions (cached)
        permissions = await get_user_permissions_cached(
            current_user.id,
            agency_id,
            permission_service
        )
        
        # Check if user has required permission
        if permission_name not in permissions:
            logger.warning(
                f"Permission denied: user {current_user.id} lacks '{permission_name}' "
                f"in agency {agency_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You don't have permission to perform this action. Required: {permission_name}"
            )
        
        # Store agency_id in request state for downstream use
        request.state.agency_id = agency_id
        
        logger.debug(
            f"Permission granted: user {current_user.id} has '{permission_name}' "
            f"in agency {agency_id}"
        )
    
    return check_permission


def require_role(role_name: str):
    """
    Dependency factory to require specific role.
    
    Usage:
        @router.post("/invite-agent")
        async def invite_agent(
            current_user: AuthUser = Depends(get_current_user),
            _: None = Depends(require_role("agency_admin"))
        ):
            ...
    
    Args:
        role_name: Role name (e.g., "agency_admin")
        
    Returns:
        FastAPI dependency function
    """
    async def check_role(
        request: Request,
        current_user: AuthUser = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        """Check if current user has required role."""
        # Extract agency_id
        agency_id = await extract_agency_id_from_request(request)
        
        if not agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency ID is required for this operation"
            )
        
        # Check if user has role
        has_role = await permission_service.has_role(
            current_user.id,
            agency_id,
            role_name
        )
        
        if not has_role:
            logger.warning(
                f"Role check failed: user {current_user.id} lacks role '{role_name}' "
                f"in agency {agency_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You must be a '{role_name}' to perform this action"
            )
        
        # Store agency_id in request state
        request.state.agency_id = agency_id
        
        logger.debug(
            f"Role check passed: user {current_user.id} has role '{role_name}' "
            f"in agency {agency_id}"
        )
    
    return check_role


def require_any_permission(*permission_names: str):
    """
    Dependency factory to require ANY of the specified permissions.
    
    Usage:
        @router.get("/contacts/{contact_id}")
        async def get_contact(
            _: None = Depends(require_any_permission("contacts.view", "contacts.edit"))
        ):
            ...
    
    Args:
        *permission_names: Multiple permission names
        
    Returns:
        FastAPI dependency function
    """
    async def check_any_permission(
        request: Request,
        current_user: AuthUser = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        """Check if user has ANY of the required permissions."""
        agency_id = await extract_agency_id_from_request(request)
        
        if not agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency ID is required"
            )
        
        # Get user permissions
        permissions = await get_user_permissions_cached(
            current_user.id,
            agency_id,
            permission_service
        )
        
        # Check if user has ANY of the required permissions
        has_any = any(perm in permissions for perm in permission_names)
        
        if not has_any:
            logger.warning(
                f"Permission denied: user {current_user.id} lacks any of {permission_names}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You need one of these permissions: {', '.join(permission_names)}"
            )
        
        request.state.agency_id = agency_id
    
    return check_any_permission


def require_all_permissions(*permission_names: str):
    """
    Dependency factory to require ALL of the specified permissions.
    
    Args:
        *permission_names: Multiple permission names
        
    Returns:
        FastAPI dependency function
    """
    async def check_all_permissions(
        request: Request,
        current_user: AuthUser = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        """Check if user has ALL of the required permissions."""
        agency_id = await extract_agency_id_from_request(request)
        
        if not agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency ID is required"
            )
        
        # Get user permissions
        permissions = await get_user_permissions_cached(
            current_user.id,
            agency_id,
            permission_service
        )
        
        # Check if user has ALL required permissions
        missing = [perm for perm in permission_names if perm not in permissions]
        
        if missing:
            logger.warning(
                f"Permission denied: user {current_user.id} lacks {missing}"
            )
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"You lack these permissions: {', '.join(missing)}"
            )
        
        request.state.agency_id = agency_id
    
    return check_all_permissions


# ============================================================
# Resource Ownership Dependencies
# ============================================================

async def require_resource_access(
    resource_type: str,
    resource_id: UUID,
    required_permission: str,
    current_user: AuthUser,
    agency_id: UUID,
    permission_service: PermissionService,
    check_ownership: bool = True
) -> None:
    """
    Check if user can access specific resource.
    
    This is a complex check that verifies:
    1. User has required permission
    2. Resource belongs to user's agency (optional)
    3. User owns the resource or has permission to access others' resources
    
    Args:
        resource_type: Type of resource (e.g., "contact", "property")
        resource_id: Resource ID
        required_permission: Permission needed (e.g., "contacts.edit")
        current_user: Current authenticated user
        agency_id: Agency context
        permission_service: PermissionService instance
        check_ownership: Whether to verify resource ownership
        
    Raises:
        HTTPException: If access is denied
    """
    # Get user permissions
    permissions = await get_user_permissions_cached(
        current_user.id,
        agency_id,
        permission_service
    )
    
    # Check if user has required permission
    if required_permission not in permissions:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"You don't have permission to access this resource. Required: {required_permission}"
        )
    
    # TODO: Implement ownership check when resource services are built
    # This will check if resource belongs to agency and optionally to user
    # For now, we rely on the permission check above
    
    logger.debug(
        f"Resource access granted: user {current_user.id} can access "
        f"{resource_type} {resource_id}"
    )


def require_ownership(resource_type: str, permission_name: str):
    """
    Dependency factory to check resource ownership.
    
    Usage:
        @router.put("/contacts/{contact_id}")
        async def update_contact(
            contact_id: UUID,
            _: None = Depends(require_ownership("contact", "contacts.edit"))
        ):
            ...
    
    Args:
        resource_type: Resource type (e.g., "contact", "property")
        permission_name: Permission needed
        
    Returns:
        FastAPI dependency function
    """
    async def check_ownership(
        request: Request,
        current_user: AuthUser = Depends(get_current_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        """Check if user can access resource."""
        # Extract resource_id from path
        resource_id_str = request.path_params.get(f"{resource_type}_id")
        if not resource_id_str:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"{resource_type}_id not found in path"
            )
        
        try:
            resource_id = UUID(resource_id_str)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid {resource_type}_id format"
            )
        
        # Extract agency_id
        agency_id = await extract_agency_id_from_request(request)
        if not agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Agency ID is required"
            )
        
        # Check resource access
        await require_resource_access(
            resource_type,
            resource_id,
            permission_name,
            current_user,
            agency_id,
            permission_service
        )
        
        request.state.agency_id = agency_id
    
    return check_ownership


# ============================================================
# Utility Dependencies
# ============================================================

async def get_current_agency_id(request: Request) -> UUID:
    """
    Dependency to extract and validate agency_id.
    
    Usage:
        async def endpoint(agency_id: UUID = Depends(get_current_agency_id)):
            ...
    """
    agency_id = await extract_agency_id_from_request(request)
    
    if not agency_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agency ID is required for this operation"
        )
    
    return agency_id


async def get_user_with_permissions(
    request: Request,
    current_user: AuthUser = Depends(get_current_user),
    permission_service: PermissionService = Depends(get_permission_service)
) -> tuple[AuthUser, UUID, set[str]]:
    """
    Dependency to get user with their permissions loaded.
    
    Returns:
        Tuple of (user, agency_id, permissions)
    
    Usage:
        async def endpoint(
            user_data: tuple = Depends(get_user_with_permissions)
        ):
            user, agency_id, permissions = user_data
            ...
    """
    agency_id = await extract_agency_id_from_request(request)
    
    if not agency_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Agency ID is required"
        )
    
    permissions = await get_user_permissions_cached(
        current_user.id,
        agency_id,
        permission_service
    )
    
    request.state.agency_id = agency_id
    
    return current_user, agency_id, permissions


# ============================================================
# Programmatic Permission Checks (for use in business logic)
# ============================================================

async def check_permission_programmatic(
    user_id: UUID,
    agency_id: UUID,
    permission_name: str,
    db: AsyncSession
) -> bool:
    """
    Check permission programmatically (not as FastAPI dependency).
    
    Use this in service methods where you need to check permissions
    but aren't in a FastAPI route context.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_name: Permission name
        db: Database session
        
    Returns:
        True if user has permission, False otherwise
    """
    permission_service = PermissionService(db)
    
    # Check cache first
    cached = await permission_cache.get_user_permissions(user_id, agency_id)
    if cached is not None:
        return permission_name in cached
    
    # Load from database
    return await permission_service.check_permission(user_id, agency_id, permission_name)


async def require_permission_programmatic(
    user_id: UUID,
    agency_id: UUID,
    permission_name: str,
    db: AsyncSession
) -> None:
    """
    Require permission programmatically (raises exception if denied).
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_name: Permission name
        db: Database session
        
    Raises:
        PermissionDeniedError: If user lacks permission
    """
    has_permission = await check_permission_programmatic(
        user_id,
        agency_id,
        permission_name,
        db
    )
    
    if not has_permission:
        raise PermissionDeniedError(
            f"User lacks permission: {permission_name}"
        )

