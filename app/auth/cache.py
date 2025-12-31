"""
Authentication-specific Redis caching utilities.
"""
import logging
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from uuid import UUID

from app.core.cache import redis_cache
from app.database.models import AuthUser, Role, Permission

logger = logging.getLogger(__name__)


# Cache key patterns
class CacheKeys:
    """Cache key patterns for authentication."""
    
    USER = "auth:user:{user_id}"
    PERMISSIONS = "auth:permissions:{user_id}:{agency_id}"
    ROLES = "auth:roles:{user_id}:{agency_id}"
    TOKEN_BLACKLIST = "auth:token:blacklist:{jti}"
    REFRESH_TOKEN = "auth:refresh:{token_hash}"
    
    @staticmethod
    def user_key(user_id: UUID) -> str:
        """Get user cache key."""
        return CacheKeys.USER.format(user_id=str(user_id))
    
    @staticmethod
    def permissions_key(user_id: UUID, agency_id: UUID) -> str:
        """Get permissions cache key."""
        return CacheKeys.PERMISSIONS.format(
            user_id=str(user_id),
            agency_id=str(agency_id)
        )
    
    @staticmethod
    def roles_key(user_id: UUID, agency_id: UUID) -> str:
        """Get roles cache key."""
        return CacheKeys.ROLES.format(
            user_id=str(user_id),
            agency_id=str(agency_id)
        )
    
    @staticmethod
    def token_blacklist_key(jti: str) -> str:
        """Get token blacklist key."""
        return CacheKeys.TOKEN_BLACKLIST.format(jti=jti)
    
    @staticmethod
    def refresh_token_key(token_hash: str) -> str:
        """Get refresh token cache key."""
        return CacheKeys.REFRESH_TOKEN.format(token_hash=token_hash)


# Cache TTLs (in seconds)
class CacheTTL:
    """Cache TTL constants."""
    USER = 3600  # 1 hour
    PERMISSIONS = 3600  # 1 hour
    ROLES = 3600  # 1 hour
    REFRESH_TOKEN = 30 * 24 * 3600  # 30 days


class AuthCache:
    """Authentication cache service."""
    
    @staticmethod
    async def get_user(user_id: UUID) -> Optional[Dict[str, Any]]:
        """
        Get cached user data.
        
        Args:
            user_id: User UUID
            
        Returns:
            Cached user data or None
        """
        key = CacheKeys.user_key(user_id)
        return await redis_cache.get(key)
    
    @staticmethod
    async def set_user(user: AuthUser, ttl: int = CacheTTL.USER) -> bool:
        """
        Cache user data.
        
        Args:
            user: AuthUser instance
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = CacheKeys.user_key(user.id)
        user_data = {
            "id": str(user.id),
            "email": user.email,
            "is_active": user.is_active,
            "is_verified": user.is_verified,
            "email_verified_at": user.email_verified_at.isoformat() if user.email_verified_at else None,
            "last_login_at": user.last_login_at.isoformat() if user.last_login_at else None,
            "failed_login_attempts": user.failed_login_attempts,
            "locked_until": user.locked_until.isoformat() if user.locked_until else None,
            "created_at": user.created_at.isoformat() if user.created_at else None,
            "updated_at": user.updated_at.isoformat() if user.updated_at else None,
        }
        return await redis_cache.set(key, user_data, ttl)
    
    @staticmethod
    async def invalidate_user(user_id: UUID) -> bool:
        """
        Invalidate cached user data.
        
        Args:
            user_id: User UUID
            
        Returns:
            True if successful
        """
        key = CacheKeys.user_key(user_id)
        return await redis_cache.delete(key)
    
    @staticmethod
    async def get_permissions(
        user_id: UUID,
        agency_id: UUID
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached user permissions.
        
        Args:
            user_id: User UUID
            agency_id: Agency UUID
            
        Returns:
            Cached permissions list or None
        """
        key = CacheKeys.permissions_key(user_id, agency_id)
        return await redis_cache.get(key)
    
    @staticmethod
    async def set_permissions(
        user_id: UUID,
        agency_id: UUID,
        permissions: List[Permission],
        ttl: int = CacheTTL.PERMISSIONS
    ) -> bool:
        """
        Cache user permissions.
        
        Args:
            user_id: User UUID
            agency_id: Agency UUID
            permissions: List of Permission instances
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = CacheKeys.permissions_key(user_id, agency_id)
        permissions_data = [
            {
                "id": str(p.id),
                "name": p.name,
                "resource": p.resource,
                "action": p.action,
                "description": p.description,
            }
            for p in permissions
        ]
        return await redis_cache.set(key, permissions_data, ttl)
    
    @staticmethod
    async def invalidate_permissions(user_id: Optional[UUID] = None, agency_id: Optional[UUID] = None) -> int:
        """
        Invalidate cached permissions.
        
        Args:
            user_id: User UUID (optional, if None invalidates all)
            agency_id: Agency UUID (optional, if None invalidates all)
            
        Returns:
            Number of keys deleted
        """
        if user_id and agency_id:
            # Invalidate specific user/agency
            key = CacheKeys.permissions_key(user_id, agency_id)
            deleted = await redis_cache.delete(key)
            return 1 if deleted else 0
        else:
            # Invalidate all permissions
            pattern = CacheKeys.PERMISSIONS.replace("{user_id}", "*").replace("{agency_id}", "*")
            return await redis_cache.delete_pattern(pattern)
    
    @staticmethod
    async def get_roles(
        user_id: UUID,
        agency_id: UUID
    ) -> Optional[List[Dict[str, Any]]]:
        """
        Get cached user roles.
        
        Args:
            user_id: User UUID
            agency_id: Agency UUID
            
        Returns:
            Cached roles list or None
        """
        key = CacheKeys.roles_key(user_id, agency_id)
        return await redis_cache.get(key)
    
    @staticmethod
    async def set_roles(
        user_id: UUID,
        agency_id: UUID,
        roles: List[Role],
        ttl: int = CacheTTL.ROLES
    ) -> bool:
        """
        Cache user roles.
        
        Args:
            user_id: User UUID
            agency_id: Agency UUID
            roles: List of Role instances
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = CacheKeys.roles_key(user_id, agency_id)
        roles_data = [
            {
                "id": str(r.id),
                "name": r.name,
                "description": r.description,
                "is_system_role": r.is_system_role,
            }
            for r in roles
        ]
        return await redis_cache.set(key, roles_data, ttl)
    
    @staticmethod
    async def invalidate_roles(user_id: Optional[UUID] = None, agency_id: Optional[UUID] = None) -> int:
        """
        Invalidate cached roles.
        
        Args:
            user_id: User UUID (optional, if None invalidates all)
            agency_id: Agency UUID (optional, if None invalidates all)
            
        Returns:
            Number of keys deleted
        """
        if user_id and agency_id:
            # Invalidate specific user/agency
            key = CacheKeys.roles_key(user_id, agency_id)
            deleted = await redis_cache.delete(key)
            return 1 if deleted else 0
        else:
            # Invalidate all roles
            pattern = CacheKeys.ROLES.replace("{user_id}", "*").replace("{agency_id}", "*")
            return await redis_cache.delete_pattern(pattern)
    
    @staticmethod
    async def is_token_blacklisted(jti: str) -> bool:
        """
        Check if token is blacklisted.
        
        Args:
            jti: JWT ID (token identifier)
            
        Returns:
            True if token is blacklisted
        """
        key = CacheKeys.token_blacklist_key(jti)
        return await redis_cache.exists(key)
    
    @staticmethod
    async def blacklist_token(jti: str, ttl: int) -> bool:
        """
        Add token to blacklist.
        
        Args:
            jti: JWT ID (token identifier)
            ttl: Time to live in seconds (should match token expiry)
            
        Returns:
            True if successful
        """
        key = CacheKeys.token_blacklist_key(jti)
        # Store timestamp of blacklist
        value = {"blacklisted_at": datetime.utcnow().isoformat()}
        return await redis_cache.set(key, value, ttl)
    
    @staticmethod
    async def cache_refresh_token(token_hash: str, user_id: UUID, ttl: int = CacheTTL.REFRESH_TOKEN) -> bool:
        """
        Cache refresh token validation.
        
        Args:
            token_hash: Hashed refresh token
            user_id: User UUID
            ttl: Time to live in seconds
            
        Returns:
            True if successful
        """
        key = CacheKeys.refresh_token_key(token_hash)
        value = {
            "user_id": str(user_id),
            "cached_at": datetime.utcnow().isoformat()
        }
        return await redis_cache.set(key, value, ttl)
    
    @staticmethod
    async def get_refresh_token(token_hash: str) -> Optional[Dict[str, Any]]:
        """
        Get cached refresh token data.
        
        Args:
            token_hash: Hashed refresh token
            
        Returns:
            Cached refresh token data or None
        """
        key = CacheKeys.refresh_token_key(token_hash)
        return await redis_cache.get(key)
    
    @staticmethod
    async def invalidate_refresh_token(token_hash: str) -> bool:
        """
        Invalidate cached refresh token.
        
        Args:
            token_hash: Hashed refresh token
            
        Returns:
            True if successful
        """
        key = CacheKeys.refresh_token_key(token_hash)
        return await redis_cache.delete(key)

