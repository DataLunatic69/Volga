"""
FastAPI Dependencies for Authentication and Authorization.

All FastAPI-specific dependencies live here.
For programmatic permission checks (in services), use app/auth/permissions.py.
"""
from typing import Optional, Set, Tuple
from uuid import UUID
import logging

from fastapi import Depends, Request, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import (
    AuthUser, AgencyUser, Agency, Role, 
    Permission, UserRole as UserRoleAssignment
)
from app.auth.jwt import verify_token
from app.auth.cache import AuthCache, permission_cache
from app.auth.rbac import PermissionService
from app.auth.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
)

logger = logging.getLogger(__name__)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


# ============================================================
# Core Authentication Dependencies
# ============================================================

async def get_user_from_token(user_id: str) -> Optional[AuthUser]:
    """Helper to get user from token (used by middleware)."""
    from app.database.session import get_async_session_context
    
    try:
        uid = UUID(user_id)
        cached_user = await AuthCache.get_user(uid)
        if cached_user:
            return AuthUser(
                id=uid,
                email=cached_user["email"],
                is_active=cached_user["is_active"],
                is_verified=cached_user["is_verified"],
            )
        
        async with get_async_session_context() as db:
            result = await db.execute(select(AuthUser).where(AuthUser.id == uid))
            return result.scalar_one_or_none()
    except Exception:
        return None


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AuthUser:
    """
    Get current authenticated user from JWT token.
    
    Raises:
        HTTPException 401: If not authenticated or token invalid
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        payload = await verify_token(credentials.credentials)
        user_id = UUID(payload.get("sub"))
        jti = payload.get("jti")
        
        # Check blacklist
        if jti and await AuthCache.is_token_blacklisted(jti):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
            )
        
        # Try cache first
        cached_user = await AuthCache.get_user(user_id)
        if cached_user:
            user = AuthUser(
                id=user_id,
                email=cached_user["email"],
                is_active=cached_user["is_active"],
                is_verified=cached_user["is_verified"],
                email_verified_at=cached_user.get("email_verified_at"),
                last_login_at=cached_user.get("last_login_at"),
                failed_login_attempts=cached_user.get("failed_login_attempts", 0),
                locked_until=cached_user.get("locked_until"),
            )
            return user
        
        # Fetch from database
        result = await db.execute(select(AuthUser).where(AuthUser.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        
        await AuthCache.set_user(user)
        return user
        
    except (InvalidTokenError, TokenExpiredError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
        )


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[AuthUser]:
    """Get current user if authenticated, None otherwise."""
    if not credentials:
        return None
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None


async def get_current_active_user(
    current_user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """Get current user (must be active)."""
    if not current_user.is_active:
        logger.warning(f"Inactive user attempted access: {current_user.id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive")
    return current_user


async def get_current_verified_user(
    current_user: AuthUser = Depends(get_current_active_user)
) -> AuthUser:
    """Get current user (must be active AND verified)."""
    if not current_user.is_verified:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Email verification required")
    return current_user


async def get_optional_verified_user(
    current_user: Optional[AuthUser] = Depends(get_optional_current_user)
) -> Optional[AuthUser]:
    """Get verified user if authenticated, None otherwise."""
    if current_user and current_user.is_active and current_user.is_verified:
        return current_user
    return None


# ============================================================
# Role-Based User Dependencies
# ============================================================

async def get_current_admin_user(
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AuthUser:
    """Get current user (must have agency_admin role in ANY agency)."""
    result = await db.execute(
        select(UserRoleAssignment)
        .join(Role, UserRoleAssignment.role_id == Role.id)
        .where(
            UserRoleAssignment.user_id == current_user.id,
            Role.name == "agency_admin"
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")
    return current_user


async def get_current_superuser(
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AuthUser:
    """Get current user (must have super_admin role)."""
    result = await db.execute(
        select(UserRoleAssignment)
        .join(Role, UserRoleAssignment.role_id == Role.id)
        .where(
            UserRoleAssignment.user_id == current_user.id,
            Role.name == "super_admin"
        )
    )
    if not result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Superuser access required")
    return current_user


# ============================================================
# Agency Context Dependencies  
# ============================================================

async def extract_agency_id(request: Request) -> Optional[UUID]:
    """
    Extract agency_id from request (path, query, body, state).
    Returns None if not found.
    """
    # Path params
    agency_id = request.path_params.get("agency_id")
    if agency_id:
        try:
            return UUID(agency_id)
        except ValueError:
            pass
    
    # Query params
    agency_id = request.query_params.get("agency_id")
    if agency_id:
        try:
            return UUID(agency_id)
        except ValueError:
            pass
    
    # Request state
    if hasattr(request.state, "agency_id"):
        return request.state.agency_id
    
    # Body (POST/PUT/PATCH)
    if request.method in ["POST", "PUT", "PATCH"]:
        try:
            body = await request.json()
            agency_id = body.get("agency_id")
            if agency_id:
                return UUID(agency_id)
        except Exception:
            pass
    
    return None


async def get_required_agency_id(request: Request) -> UUID:
    """Extract agency_id (required, raises 400 if missing)."""
    agency_id = await extract_agency_id(request)
    if not agency_id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agency_id is required")
    return agency_id


async def verify_agency_membership(
    agency_id: UUID,
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> AgencyUser:
    """Verify user belongs to agency, return AgencyUser."""
    result = await db.execute(
        select(AgencyUser).where(
            AgencyUser.auth_user_id == current_user.id,
            AgencyUser.agency_id == agency_id,
            AgencyUser.is_active == True
        )
    )
    agency_user = result.scalar_one_or_none()
    
    if not agency_user:
        logger.warning(f"User {current_user.id} denied access to agency {agency_id}")
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not a member of this agency")
    
    return agency_user


async def get_agency_or_404(
    agency_id: UUID,
    db: AsyncSession = Depends(get_db)
) -> Agency:
    """Get agency by ID or raise 404."""
    result = await db.execute(select(Agency).where(Agency.id == agency_id))
    agency = result.scalar_one_or_none()
    
    if not agency:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Agency not found")
    
    return agency


async def get_current_agency(
    agency_id: UUID,
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Agency:
    """Get agency (verified user belongs to it)."""
    await verify_agency_membership(agency_id, current_user, db)
    return await get_agency_or_404(agency_id, db)


async def get_user_with_agency(
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Tuple[AuthUser, Agency]:
    """Get user and their agency context."""
    agency_id = await get_required_agency_id(request)
    agency = await get_current_agency(agency_id, current_user, db)
    request.state.agency_id = agency_id
    return current_user, agency


# ============================================================
# Permission Dependencies (FastAPI-specific)
# ============================================================

async def get_permission_service(db: AsyncSession = Depends(get_db)) -> PermissionService:
    """Dependency to get PermissionService."""
    return PermissionService(db)


def require_permission(permission_name: str):
    """
    Dependency factory to require specific permission.
    
    Usage:
        @router.get("/contacts")
        async def get_contacts(
            _: None = Depends(require_permission("contacts.view"))
        ):
            ...
    """
    async def check_permission(
        request: Request,
        current_user: AuthUser = Depends(get_current_active_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        agency_id = await extract_agency_id(request)
        
        if not agency_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agency_id required")
        
        # Get permissions (cached)
        cached = await permission_cache.get_user_permissions(current_user.id, agency_id)
        if cached is not None:
            permissions = cached
        else:
            permissions = await permission_service.get_user_permissions(current_user.id, agency_id)
            await permission_cache.set_user_permissions(current_user.id, agency_id, permissions)
        
        if permission_name not in permissions:
            logger.warning(f"Permission denied: user {current_user.id} lacks '{permission_name}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_name}"
            )
        
        request.state.agency_id = agency_id
    
    return check_permission


def require_role(role_name: str):
    """
    Dependency factory to require specific role.
    
    Usage:
        @router.post("/settings")
        async def update_settings(
            _: None = Depends(require_role("agency_admin"))
        ):
            ...
    """
    async def check_role(
        request: Request,
        current_user: AuthUser = Depends(get_current_active_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        agency_id = await extract_agency_id(request)
        
        if not agency_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agency_id required")
        
        has_role = await permission_service.has_role(current_user.id, agency_id, role_name)
        
        if not has_role:
            logger.warning(f"Role check failed: user {current_user.id} lacks role '{role_name}'")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role_name}"
            )
        
        request.state.agency_id = agency_id
    
    return check_role


def require_any_permission(*permission_names: str):
    """Dependency factory to require ANY of the permissions."""
    async def check_any(
        request: Request,
        current_user: AuthUser = Depends(get_current_active_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        agency_id = await extract_agency_id(request)
        if not agency_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agency_id required")
        
        permissions = await permission_service.get_user_permissions(current_user.id, agency_id)
        
        if not any(p in permissions for p in permission_names):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"One of these permissions required: {', '.join(permission_names)}"
            )
        
        request.state.agency_id = agency_id
    
    return check_any


def require_all_permissions(*permission_names: str):
    """Dependency factory to require ALL permissions."""
    async def check_all(
        request: Request,
        current_user: AuthUser = Depends(get_current_active_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        agency_id = await extract_agency_id(request)
        if not agency_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agency_id required")
        
        permissions = await permission_service.get_user_permissions(current_user.id, agency_id)
        missing = [p for p in permission_names if p not in permissions]
        
        if missing:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Missing permissions: {', '.join(missing)}"
            )
        
        request.state.agency_id = agency_id
    
    return check_all


def require_ownership(resource_type: str, permission_name: str):
    """
    Dependency factory to check resource ownership.
    
    Extracts {resource_type}_id from path and checks permission.
    """
    async def check_ownership(
        request: Request,
        current_user: AuthUser = Depends(get_current_active_user),
        permission_service: PermissionService = Depends(get_permission_service)
    ) -> None:
        # Extract resource ID
        resource_id_str = request.path_params.get(f"{resource_type}_id")
        if not resource_id_str:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"{resource_type}_id required")
        
        try:
            UUID(resource_id_str)
        except ValueError:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Invalid {resource_type}_id")
        
        agency_id = await extract_agency_id(request)
        if not agency_id:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="agency_id required")
        
        # Check permission
        permissions = await permission_service.get_user_permissions(current_user.id, agency_id)
        if permission_name not in permissions:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_name}"
            )
        
        request.state.agency_id = agency_id
    
    return check_ownership


# ============================================================
# Utility Dependencies
# ============================================================

async def get_user_with_permissions(
    request: Request,
    current_user: AuthUser = Depends(get_current_active_user),
    permission_service: PermissionService = Depends(get_permission_service)
) -> Tuple[AuthUser, UUID, Set[str]]:
    """Get user with their permissions loaded."""
    agency_id = await get_required_agency_id(request)
    
    cached = await permission_cache.get_user_permissions(current_user.id, agency_id)
    if cached is not None:
        permissions = cached
    else:
        permissions = await permission_service.get_user_permissions(current_user.id, agency_id)
        await permission_cache.set_user_permissions(current_user.id, agency_id, permissions)
    
    request.state.agency_id = agency_id
    return current_user, agency_id, permissions
