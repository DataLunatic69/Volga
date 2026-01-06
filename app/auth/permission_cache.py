"""
Permission Cache - Redis caching for RBAC.

Caches:
- User permissions per agency
- User roles per agency
- Complex permission checks
- Agency context

Cache invalidation happens on:
- Role assignment/revocation
- Permission changes
- Role-permission updates
"""
import json
from typing import Set, List, Optional, Dict
from uuid import UUID
import logging

from app.core.cache import redis_cache
from app.database.models import Role

logger = logging.getLogger(__name__)


class PermissionCache:
    """Redis cache for permission system."""
    
    # TTL values (in seconds)
    PERMISSION_TTL = 3600  # 1 hour
    ROLE_TTL = 3600  # 1 hour
    CHECK_TTL = 600  # 10 minutes (for complex checks)
    AGENCY_TTL = 3600  # 1 hour
    
    # Key prefixes
    PREFIX_PERMISSIONS = "auth:permissions"
    PREFIX_ROLES = "auth:roles"
    PREFIX_CAN_ACCESS = "auth:can_access"
    PREFIX_AGENCY = "auth:agency"
    
    @classmethod
    def _make_key(cls, *parts: str) -> str:
        """Create cache key from parts."""
        return ":".join(str(p) for p in parts)
    
    # ============================================================
    # User Permissions Cache
    # ============================================================
    
    @classmethod
    async def get_user_permissions(
        cls,
        user_id: UUID,
        agency_id: UUID
    ) -> Optional[Set[str]]:
        """
        Get cached user permissions.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            
        Returns:
            Set of permission names or None if not cached
        """
        key = cls._make_key(cls.PREFIX_PERMISSIONS, user_id, agency_id)
        
        try:
            value = await redis_cache.get(key)
            if value:
                permissions_list = json.loads(value)
                return set(permissions_list)
        except Exception as e:
            logger.error(f"Error getting cached permissions: {e}")
        
        return None
    
    @classmethod
    async def set_user_permissions(
        cls,
        user_id: UUID,
        agency_id: UUID,
        permissions: Set[str]
    ) -> bool:
        """
        Cache user permissions.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            permissions: Set of permission names
            
        Returns:
            True if cached successfully
        """
        key = cls._make_key(cls.PREFIX_PERMISSIONS, user_id, agency_id)
        
        try:
            # Convert set to list for JSON serialization
            permissions_list = list(permissions)
            value = json.dumps(permissions_list)
            
            await redis_cache.set(key, value, ttl=cls.PERMISSION_TTL)
            logger.debug(f"Cached {len(permissions)} permissions for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching permissions: {e}")
            return False
    
    @classmethod
    async def invalidate_user_permissions(
        cls,
        user_id: UUID,
        agency_id: Optional[UUID] = None
    ) -> None:
        """
        Invalidate cached permissions for user.
        
        Args:
            user_id: User ID
            agency_id: Agency ID (if None, invalidate all agencies)
        """
        try:
            if agency_id:
                # Invalidate specific agency
                key = cls._make_key(cls.PREFIX_PERMISSIONS, user_id, agency_id)
                await redis_cache.delete(key)
                logger.debug(f"Invalidated permissions for user {user_id} in agency {agency_id}")
            else:
                # Invalidate all agencies for user
                pattern = cls._make_key(cls.PREFIX_PERMISSIONS, user_id, "*")
                await redis_cache.delete_pattern(pattern)
                logger.debug(f"Invalidated all permissions for user {user_id}")
        except Exception as e:
            logger.error(f"Error invalidating permissions cache: {e}")
    
    # ============================================================
    # User Roles Cache
    # ============================================================
    
    @classmethod
    async def get_user_roles(
        cls,
        user_id: UUID,
        agency_id: UUID
    ) -> Optional[List[str]]:
        """
        Get cached user role names.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            
        Returns:
            List of role names or None if not cached
        """
        key = cls._make_key(cls.PREFIX_ROLES, user_id, agency_id)
        
        try:
            value = await redis_cache.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting cached roles: {e}")
        
        return None
    
    @classmethod
    async def set_user_roles(
        cls,
        user_id: UUID,
        agency_id: UUID,
        roles: List[Role]
    ) -> bool:
        """
        Cache user roles.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            roles: List of Role objects
            
        Returns:
            True if cached successfully
        """
        key = cls._make_key(cls.PREFIX_ROLES, user_id, agency_id)
        
        try:
            # Store just the role names
            role_names = [role.name for role in roles]
            value = json.dumps(role_names)
            
            await redis_cache.set(key, value, ttl=cls.ROLE_TTL)
            logger.debug(f"Cached {len(role_names)} roles for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Error caching roles: {e}")
            return False
    
    @classmethod
    async def invalidate_user_roles(
        cls,
        user_id: UUID,
        agency_id: Optional[UUID] = None
    ) -> None:
        """
        Invalidate cached roles for user.
        
        Args:
            user_id: User ID
            agency_id: Agency ID (if None, invalidate all agencies)
        """
        try:
            if agency_id:
                key = cls._make_key(cls.PREFIX_ROLES, user_id, agency_id)
                await redis_cache.delete(key)
            else:
                pattern = cls._make_key(cls.PREFIX_ROLES, user_id, "*")
                await redis_cache.delete_pattern(pattern)
            logger.debug(f"Invalidated roles cache for user {user_id}")
        except Exception as e:
            logger.error(f"Error invalidating roles cache: {e}")
    
    # ============================================================
    # Complex Permission Checks Cache
    # ============================================================
    
    @classmethod
    async def get_can_access(
        cls,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID
    ) -> Optional[bool]:
        """
        Get cached complex permission check result.
        
        Example: "Can user 123 edit contact 456?"
        
        Args:
            user_id: User ID
            resource_type: Resource type (e.g., "contact", "property")
            resource_id: Resource ID
            
        Returns:
            True/False if cached, None if not cached
        """
        key = cls._make_key(cls.PREFIX_CAN_ACCESS, user_id, resource_type, resource_id)
        
        try:
            value = await redis_cache.get(key)
            if value is not None:
                return value == "1"
        except Exception as e:
            logger.error(f"Error getting cached access check: {e}")
        
        return None
    
    @classmethod
    async def set_can_access(
        cls,
        user_id: UUID,
        resource_type: str,
        resource_id: UUID,
        can_access: bool
    ) -> bool:
        """
        Cache complex permission check result.
        
        Args:
            user_id: User ID
            resource_type: Resource type
            resource_id: Resource ID
            can_access: Whether user can access
            
        Returns:
            True if cached successfully
        """
        key = cls._make_key(cls.PREFIX_CAN_ACCESS, user_id, resource_type, resource_id)
        
        try:
            value = "1" if can_access else "0"
            await redis_cache.set(key, value, ttl=cls.CHECK_TTL)
            return True
        except Exception as e:
            logger.error(f"Error caching access check: {e}")
            return False
    
    @classmethod
    async def invalidate_resource_access(
        cls,
        resource_type: str,
        resource_id: UUID
    ) -> None:
        """
        Invalidate all access checks for a resource.
        
        Called when resource ownership or permissions change.
        
        Args:
            resource_type: Resource type
            resource_id: Resource ID
        """
        try:
            pattern = cls._make_key(cls.PREFIX_CAN_ACCESS, "*", resource_type, resource_id)
            await redis_cache.delete_pattern(pattern)
            logger.debug(f"Invalidated access cache for {resource_type} {resource_id}")
        except Exception as e:
            logger.error(f"Error invalidating resource access cache: {e}")
    
    # ============================================================
    # Agency Context Cache
    # ============================================================
    
    @classmethod
    async def get_agency_context(cls, agency_id: UUID) -> Optional[Dict]:
        """
        Get cached agency context.
        
        Includes: settings, subscription tier, business hours, AI config
        
        Args:
            agency_id: Agency ID
            
        Returns:
            Agency context dict or None if not cached
        """
        key = cls._make_key(cls.PREFIX_AGENCY, agency_id)
        
        try:
            value = await redis_cache.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.error(f"Error getting cached agency context: {e}")
        
        return None
    
    @classmethod
    async def set_agency_context(
        cls,
        agency_id: UUID,
        context: Dict
    ) -> bool:
        """
        Cache agency context.
        
        Args:
            agency_id: Agency ID
            context: Agency context dictionary
            
        Returns:
            True if cached successfully
        """
        key = cls._make_key(cls.PREFIX_AGENCY, agency_id)
        
        try:
            value = json.dumps(context)
            await redis_cache.set(key, value, ttl=cls.AGENCY_TTL)
            return True
        except Exception as e:
            logger.error(f"Error caching agency context: {e}")
            return False
    
    @classmethod
    async def invalidate_agency_context(cls, agency_id: UUID) -> None:
        """
        Invalidate cached agency context.
        
        Args:
            agency_id: Agency ID
        """
        try:
            key = cls._make_key(cls.PREFIX_AGENCY, agency_id)
            await redis_cache.delete(key)
            logger.debug(f"Invalidated agency context for {agency_id}")
        except Exception as e:
            logger.error(f"Error invalidating agency context: {e}")
    
    # ============================================================
    # Bulk Invalidation
    # ============================================================
    
    @classmethod
    async def invalidate_all_for_user(
        cls,
        user_id: UUID,
        agency_id: Optional[UUID] = None
    ) -> None:
        """
        Invalidate all caches related to a user.
        
        Called when user roles change or user is deleted.
        
        Args:
            user_id: User ID
            agency_id: Agency ID (if None, invalidate across all agencies)
        """
        await cls.invalidate_user_permissions(user_id, agency_id)
        await cls.invalidate_user_roles(user_id, agency_id)
        
        # Invalidate all access checks for this user
        try:
            pattern = cls._make_key(cls.PREFIX_CAN_ACCESS, user_id, "*")
            await redis_cache.delete_pattern(pattern)
        except Exception as e:
            logger.error(f"Error invalidating user access checks: {e}")
    
    @classmethod
    async def invalidate_all_for_role(cls, role_id: UUID) -> None:
        """
        Invalidate all caches when role permissions change.
        
        This is expensive but necessary for correctness.
        
        Args:
            role_id: Role ID
        """
        try:
            # Invalidate all permissions (brute force)
            pattern = cls._make_key(cls.PREFIX_PERMISSIONS, "*")
            await redis_cache.delete_pattern(pattern)
            
            # Invalidate all access checks
            pattern = cls._make_key(cls.PREFIX_CAN_ACCESS, "*")
            await redis_cache.delete_pattern(pattern)
            
            logger.warning(f"Invalidated all permission caches due to role {role_id} change")
        except Exception as e:
            logger.error(f"Error invalidating role caches: {e}")
    
    @classmethod
    async def invalidate_all_for_agency(cls, agency_id: UUID) -> None:
        """
        Invalidate all caches for an agency.
        
        Called when agency is deleted or permissions restructured.
        
        Args:
            agency_id: Agency ID
        """
        try:
            # Invalidate all permissions for agency
            pattern = cls._make_key(cls.PREFIX_PERMISSIONS, "*", agency_id)
            await redis_cache.delete_pattern(pattern)
            
            # Invalidate all roles for agency
            pattern = cls._make_key(cls.PREFIX_ROLES, "*", agency_id)
            await redis_cache.delete_pattern(pattern)
            
            # Invalidate agency context
            await cls.invalidate_agency_context(agency_id)
            
            logger.info(f"Invalidated all caches for agency {agency_id}")
        except Exception as e:
            logger.error(f"Error invalidating agency caches: {e}")


# Convenience singleton instance
permission_cache = PermissionCache()

