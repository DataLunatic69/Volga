"""
FastAPI dependencies for authentication and authorization.
"""
from typing import Optional
from uuid import UUID

from fastapi import Depends, HTTPException, status, Header
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.database.models import AuthUser, AgencyUser, Agency, Role, Permission, UserRole as UserRoleAssignment
from app.auth.jwt import verify_token, decode_token
from app.auth.cache import AuthCache
from app.auth.exceptions import (
    InvalidTokenError,
    TokenExpiredError,
    UserInactiveError,
    UserNotVerifiedError,
)

# HTTP Bearer token scheme
security = HTTPBearer(auto_error=False)


async def get_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> AuthUser:
    """
    Get current authenticated user from JWT token.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Authenticated user
        
    Raises:
        HTTPException: If token is invalid or user not found
    """
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    token = credentials.credentials
    
    try:
        # Verify and decode token (async - includes blacklist check)
        payload = await verify_token(token)
        user_id = UUID(payload.get("sub"))
        jti = payload.get("jti")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has been revoked",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        # Try to get user from cache first
        cached_user = await AuthCache.get_user(user_id)
        if cached_user:
            # Reconstruct AuthUser from cache
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
        
        # Cache miss - fetch from database
        result = await db.execute(
            select(AuthUser).where(AuthUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found"
            )
        
        # Cache user for future requests
        await AuthCache.set_user(user)
        
        return user
        
    except (InvalidTokenError, TokenExpiredError, ValueError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"Invalid token: {str(e)}",
            headers={"WWW-Authenticate": "Bearer"},
        )


async def get_current_active_user(
    current_user: AuthUser = Depends(get_current_user)
) -> AuthUser:
    """
    Get current active user (must be active).
    
    Args:
        current_user: Current authenticated user
        
    Returns:
        Active user
        
    Raises:
        HTTPException: If user is inactive
    """
    if not current_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    return current_user


async def get_current_verified_user(
    current_user: AuthUser = Depends(get_current_active_user)
) -> AuthUser:
    """
    Get current verified user (must be active and verified).
    
    Args:
        current_user: Current active user
        
    Returns:
        Verified user
        
    Raises:
        HTTPException: If user email is not verified
    """
    if not current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Email verification required"
        )
    return current_user


async def get_current_agency(
    agency_id: UUID,
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
) -> Agency:
    """
    Get agency and verify user belongs to it.
    
    Args:
        agency_id: Agency UUID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Agency
        
    Raises:
        HTTPException: If user doesn't belong to agency
    """
    # Check if user belongs to agency
    result = await db.execute(
        select(AgencyUser).where(
            AgencyUser.auth_user_id == current_user.id,
            AgencyUser.agency_id == agency_id,
            AgencyUser.is_active == True
        )
    )
    agency_user = result.scalar_one_or_none()
    
    if not agency_user:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not belong to this agency"
        )
    
    # Fetch agency
    result = await db.execute(
        select(Agency).where(Agency.id == agency_id)
    )
    agency = result.scalar_one()
    
    return agency


def require_permission(permission_name: str):
    """
    Dependency factory for permission checking.
    
    Args:
        permission_name: Required permission (e.g., "contacts.view")
        
    Returns:
        Dependency function
    """
    async def permission_checker(
        current_user: AuthUser = Depends(get_current_active_user),
        agency_id: Optional[UUID] = None,
        db: AsyncSession = Depends(get_db)
    ) -> None:
        """
        Check if user has required permission.
        
        Raises:
            HTTPException: If user doesn't have permission
        """
        if not agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="agency_id is required for permission check"
            )
        
        # TODO: Implement permission checking logic
        # For now, we'll do a basic check
        # This will be enhanced when PermissionService is implemented
        
        # Check if user has role in agency
        result = await db.execute(
            select(UserRoleAssignment).where(
                UserRoleAssignment.user_id == current_user.id,
                UserRoleAssignment.agency_id == agency_id
            )
        )
        user_roles = result.scalars().all()
        
        if not user_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission denied: {permission_name}"
            )
        
        # TODO: Check actual permissions via PermissionService
        # For now, allow if user has any role in agency
    
    return permission_checker


def require_role(role_name: str):
    """
    Dependency factory for role checking.
    
    Args:
        role_name: Required role (e.g., "agency_admin")
        
    Returns:
        Dependency function
    """
    async def role_checker(
        current_user: AuthUser = Depends(get_current_active_user),
        agency_id: Optional[UUID] = None,
        db: AsyncSession = Depends(get_db)
    ) -> None:
        """
        Check if user has required role.
        
        Raises:
            HTTPException: If user doesn't have role
        """
        if not agency_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="agency_id is required for role check"
            )
        
        # Get user's roles in agency
        result = await db.execute(
            select(UserRoleAssignment, Role).join(
                Role, UserRoleAssignment.role_id == Role.id
            ).where(
                UserRoleAssignment.user_id == current_user.id,
                UserRoleAssignment.agency_id == agency_id
            )
        )
        user_roles = result.all()
        
        # Check if user has required role
        has_role = any(
            role.name == role_name for _, role in user_roles
        )
        
        if not has_role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Role required: {role_name}"
            )
    
    return role_checker


async def get_optional_current_user(
    credentials: Optional[HTTPAuthorizationCredentials] = Depends(security),
    db: AsyncSession = Depends(get_db)
) -> Optional[AuthUser]:
    """
    Get current user if authenticated, otherwise return None.
    Useful for endpoints that work both authenticated and unauthenticated.
    
    Args:
        credentials: HTTP Bearer token credentials
        db: Database session
        
    Returns:
        Authenticated user or None
    """
    if not credentials:
        return None
    
    try:
        return await get_current_user(credentials, db)
    except HTTPException:
        return None

