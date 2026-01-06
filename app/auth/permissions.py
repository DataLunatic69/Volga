"""
Permission Business Logic - Programmatic permission checks (NO FastAPI dependencies).

This module contains pure business logic for permission checking.
For FastAPI dependencies, use app/auth/dependencies.py instead.

Usage in services/business logic:
    from app.auth.permissions import check_permission, require_permission
    
    has_access = await check_permission(user_id, agency_id, "contacts.view", db)
    await require_permission(user_id, agency_id, "contacts.edit", db)
"""
from typing import Set, List, Optional
from uuid import UUID
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.rbac import PermissionService
from app.auth.cache import permission_cache
from app.auth.exceptions import PermissionDeniedError

logger = logging.getLogger(__name__)


# ============================================================
# Permission Checking (Pure Business Logic)
# ============================================================

async def get_user_permissions_cached(
    user_id: UUID,
    agency_id: UUID,
    db: AsyncSession
) -> Set[str]:
    """
    Get user permissions with caching.
    
    Args:
        user_id: User ID
        agency_id: Agency ID  
        db: Database session
        
    Returns:
        Set of permission names
    """
    # Try cache first
    cached = await permission_cache.get_user_permissions(user_id, agency_id)
    if cached is not None:
        logger.debug(f"Cache hit: permissions for user {user_id}")
        return cached
    
    # Cache miss - load from database
    logger.debug(f"Cache miss: loading permissions for user {user_id}")
    permission_service = PermissionService(db)
    permissions = await permission_service.get_user_permissions(user_id, agency_id)
    
    # Cache for future requests
    await permission_cache.set_user_permissions(user_id, agency_id, permissions)
    
    return permissions


async def check_permission(
    user_id: UUID,
    agency_id: UUID,
    permission_name: str,
    db: AsyncSession
) -> bool:
    """
    Check if user has permission (programmatic, no FastAPI).
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_name: Permission name (e.g., "contacts.view")
        db: Database session
        
    Returns:
        True if user has permission
    """
    permissions = await get_user_permissions_cached(user_id, agency_id, db)
    return permission_name in permissions


async def require_permission(
    user_id: UUID,
    agency_id: UUID,
    permission_name: str,
    db: AsyncSession
) -> None:
    """
    Require user to have permission, raise if not.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_name: Permission name
        db: Database session
        
    Raises:
        PermissionDeniedError: If user lacks permission
    """
    has_perm = await check_permission(user_id, agency_id, permission_name, db)
    
    if not has_perm:
        logger.warning(f"Permission denied: user {user_id} lacks '{permission_name}' in agency {agency_id}")
        raise PermissionDeniedError(f"Permission denied: {permission_name}")


async def check_any_permission(
    user_id: UUID,
    agency_id: UUID,
    permission_names: List[str],
    db: AsyncSession
) -> bool:
    """
    Check if user has ANY of the permissions.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_names: List of permission names
        db: Database session
        
    Returns:
        True if user has any of the permissions
    """
    permissions = await get_user_permissions_cached(user_id, agency_id, db)
    return any(perm in permissions for perm in permission_names)


async def check_all_permissions(
    user_id: UUID,
    agency_id: UUID,
    permission_names: List[str],
    db: AsyncSession
) -> bool:
    """
    Check if user has ALL of the permissions.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        permission_names: List of permission names
        db: Database session
        
    Returns:
        True if user has all permissions
    """
    permissions = await get_user_permissions_cached(user_id, agency_id, db)
    return all(perm in permissions for perm in permission_names)


async def check_role(
    user_id: UUID,
    agency_id: UUID,
    role_name: str,
    db: AsyncSession
) -> bool:
    """
    Check if user has specific role.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        role_name: Role name (e.g., "agency_admin")
        db: Database session
        
    Returns:
        True if user has role
    """
    permission_service = PermissionService(db)
    return await permission_service.has_role(user_id, agency_id, role_name)


async def require_role(
    user_id: UUID,
    agency_id: UUID,
    role_name: str,
    db: AsyncSession
) -> None:
    """
    Require user to have role, raise if not.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        role_name: Role name
        db: Database session
        
    Raises:
        PermissionDeniedError: If user lacks role
    """
    has = await check_role(user_id, agency_id, role_name, db)
    
    if not has:
        logger.warning(f"Role check failed: user {user_id} lacks role '{role_name}'")
        raise PermissionDeniedError(f"Role required: {role_name}")


async def get_user_roles(
    user_id: UUID,
    agency_id: UUID,
    db: AsyncSession
) -> List[str]:
    """
    Get user's role names in agency.
    
    Args:
        user_id: User ID
        agency_id: Agency ID
        db: Database session
        
    Returns:
        List of role names
    """
    # Try cache first
    cached = await permission_cache.get_user_roles(user_id, agency_id)
    if cached is not None:
        return cached
    
    # Load from database
    permission_service = PermissionService(db)
    roles = await permission_service.get_user_roles(user_id, agency_id)
    role_names = [r.name for r in roles]
    
    # Cache
    await permission_cache.set_user_roles(user_id, agency_id, roles)
    
    return role_names


# ============================================================
# Cache Invalidation Helpers
# ============================================================

async def invalidate_user_permissions(
    user_id: UUID,
    agency_id: Optional[UUID] = None
) -> None:
    """
    Invalidate cached permissions for user.
    
    Call this after role/permission changes.
    """
    await permission_cache.invalidate_all_for_user(user_id, agency_id)


async def invalidate_role_permissions(role_id: UUID) -> None:
    """
    Invalidate all caches when role permissions change.
    """
    await permission_cache.invalidate_all_for_role(role_id)
