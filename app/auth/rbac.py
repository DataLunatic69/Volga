"""
Permission Service - Core RBAC business logic.

Handles:
- Permission checks
- Role assignments
- Permission cache management
- Role-permission relationships
"""
from datetime import datetime, timezone
from typing import List, Optional, Set, Dict
from uuid import UUID
import logging

from sqlalchemy import select, delete, and_, or_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.database.models import (
    Permission,
    Role,
    RolePermission,
    UserRole as UserRoleAssignment,
    AuthUser,
    Agency
)
from app.auth.exceptions import (
    PermissionDeniedError,
    ResourceNotFoundError,
    InvalidInputError
)

logger = logging.getLogger(__name__)


class PermissionService:
    """Service for managing permissions and roles."""
    
    def __init__(self, db: AsyncSession):
        self.db = db
    
    # ============================================================
    # Permission Checking (Core RBAC Logic)
    # ============================================================
    
    async def check_permission(
        self,
        user_id: UUID,
        agency_id: UUID,
        permission_name: str
    ) -> bool:
        """
        Check if user has specific permission in agency.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            permission_name: Permission name (e.g., "contacts.view")
            
        Returns:
            True if user has permission, False otherwise
        """
        try:
            permissions = await self.get_user_permissions(user_id, agency_id)
            return permission_name in permissions
        except Exception as e:
            logger.error(f"Error checking permission for user {user_id}: {e}")
            return False
    
    async def require_permission(
        self,
        user_id: UUID,
        agency_id: UUID,
        permission_name: str
    ) -> None:
        """
        Require user to have permission, raise exception if not.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            permission_name: Permission name
            
        Raises:
            PermissionDeniedError: If user lacks permission
        """
        has_permission = await self.check_permission(user_id, agency_id, permission_name)
        
        if not has_permission:
            logger.warning(
                f"Permission denied: user {user_id} lacks '{permission_name}' "
                f"in agency {agency_id}"
            )
            raise PermissionDeniedError(
                f"You don't have permission to perform this action. "
                f"Required: {permission_name}"
            )
    
    async def get_user_permissions(
        self,
        user_id: UUID,
        agency_id: UUID,
        include_expired: bool = False
    ) -> Set[str]:
        """
        Get all permissions for user in agency.
        
        This is the core method that loads user permissions by:
        1. Finding all user's roles in the agency
        2. Loading all permissions for those roles
        3. Returning unique set of permission names
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            include_expired: Whether to include expired role assignments
            
        Returns:
            Set of permission names (e.g., {"contacts.view", "properties.edit"})
        """
        # Build query for user's roles in agency
        query = (
            select(Permission.name)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .join(Role, Role.id == RolePermission.role_id)
            .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
            .where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    UserRoleAssignment.agency_id == agency_id
                )
            )
        )
        
        # Exclude expired roles unless explicitly requested
        if not include_expired:
            now = datetime.now(timezone.utc)
            query = query.where(
                or_(
                    UserRoleAssignment.expires_at.is_(None),
                    UserRoleAssignment.expires_at > now
                )
            )
        
        result = await self.db.execute(query)
        permissions = result.scalars().all()
        
        return set(permissions)
    
    async def get_user_roles(
        self,
        user_id: UUID,
        agency_id: UUID,
        include_expired: bool = False
    ) -> List[Role]:
        """
        Get all roles assigned to user in agency.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            include_expired: Whether to include expired roles
            
        Returns:
            List of Role objects
        """
        query = (
            select(Role)
            .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
            .where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    UserRoleAssignment.agency_id == agency_id
                )
            )
        )
        
        if not include_expired:
            now = datetime.now(timezone.utc)
            query = query.where(
                or_(
                    UserRoleAssignment.expires_at.is_(None),
                    UserRoleAssignment.expires_at > now
                )
            )
        
        result = await self.db.execute(query)
        roles = result.scalars().all()
        
        return list(roles)
    
    async def has_role(
        self,
        user_id: UUID,
        agency_id: UUID,
        role_name: str
    ) -> bool:
        """
        Check if user has specific role in agency.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            role_name: Role name (e.g., "agency_admin")
            
        Returns:
            True if user has role, False otherwise
        """
        query = (
            select(Role.id)
            .join(UserRoleAssignment, UserRoleAssignment.role_id == Role.id)
            .where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    UserRoleAssignment.agency_id == agency_id,
                    Role.name == role_name
                )
            )
        )
        
        # Check not expired
        now = datetime.now(timezone.utc)
        query = query.where(
            or_(
                UserRoleAssignment.expires_at.is_(None),
                UserRoleAssignment.expires_at > now
            )
        )
        
        result = await self.db.execute(query)
        return result.scalar_one_or_none() is not None
    
    # ============================================================
    # Role Assignment Management
    # ============================================================
    
    async def assign_role(
        self,
        user_id: UUID,
        role_id: UUID,
        agency_id: UUID,
        granted_by: UUID,
        expires_at: Optional[datetime] = None
    ) -> UserRoleAssignment:
        """
        Assign role to user in agency.
        
        Args:
            user_id: User to assign role to
            role_id: Role to assign
            agency_id: Agency context
            granted_by: User granting the role
            expires_at: Optional expiration date
            
        Returns:
            UserRoleAssignment object
            
        Raises:
            InvalidInputError: If user, role, or agency doesn't exist
        """
        # Verify user exists
        user = await self.db.get(AuthUser, user_id)
        if not user:
            raise InvalidInputError(f"User {user_id} not found")
        
        # Verify role exists
        role = await self.db.get(Role, role_id)
        if not role:
            raise InvalidInputError(f"Role {role_id} not found")
        
        # Verify agency exists
        agency = await self.db.get(Agency, agency_id)
        if not agency:
            raise InvalidInputError(f"Agency {agency_id} not found")
        
        # Check if assignment already exists (not expired)
        existing = await self.db.execute(
            select(UserRoleAssignment).where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    UserRoleAssignment.role_id == role_id,
                    UserRoleAssignment.agency_id == agency_id,
                    or_(
                        UserRoleAssignment.expires_at.is_(None),
                        UserRoleAssignment.expires_at > datetime.now(timezone.utc)
                    )
                )
            )
        )
        existing_assignment = existing.scalar_one_or_none()
        
        if existing_assignment:
            logger.info(
                f"Role assignment already exists: user {user_id}, "
                f"role {role.name}, agency {agency_id}"
            )
            return existing_assignment
        
        # Create new assignment
        assignment = UserRoleAssignment(
            user_id=user_id,
            role_id=role_id,
            agency_id=agency_id,
            granted_by=granted_by,
            expires_at=expires_at
        )
        
        self.db.add(assignment)
        await self.db.commit()
        await self.db.refresh(assignment)
        
        logger.info(
            f"Assigned role '{role.name}' to user {user_id} "
            f"in agency {agency_id} by {granted_by}"
        )
        
        return assignment
    
    async def revoke_role(
        self,
        user_id: UUID,
        role_id: UUID,
        agency_id: UUID
    ) -> bool:
        """
        Revoke role from user in agency.
        
        Args:
            user_id: User ID
            role_id: Role ID
            agency_id: Agency ID
            
        Returns:
            True if role was revoked, False if not found
        """
        result = await self.db.execute(
            delete(UserRoleAssignment).where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    UserRoleAssignment.role_id == role_id,
                    UserRoleAssignment.agency_id == agency_id
                )
            )
        )
        
        await self.db.commit()
        
        if result.rowcount > 0:
            logger.info(
                f"Revoked role {role_id} from user {user_id} in agency {agency_id}"
            )
            return True
        
        return False
    
    async def revoke_all_roles(
        self,
        user_id: UUID,
        agency_id: UUID
    ) -> int:
        """
        Revoke all roles from user in agency.
        
        Args:
            user_id: User ID
            agency_id: Agency ID
            
        Returns:
            Number of roles revoked
        """
        result = await self.db.execute(
            delete(UserRoleAssignment).where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    UserRoleAssignment.agency_id == agency_id
                )
            )
        )
        
        await self.db.commit()
        
        logger.info(
            f"Revoked all roles from user {user_id} in agency {agency_id}. "
            f"Count: {result.rowcount}"
        )
        
        return result.rowcount
    
    # ============================================================
    # Role Management
    # ============================================================
    
    async def create_role(
        self,
        name: str,
        description: Optional[str] = None,
        is_system_role: bool = False,
        permission_ids: Optional[List[UUID]] = None
    ) -> Role:
        """
        Create new role with optional permissions.
        
        Args:
            name: Role name (must be unique)
            description: Role description
            is_system_role: Whether this is a built-in system role
            permission_ids: List of permission IDs to assign
            
        Returns:
            Created Role object
            
        Raises:
            InvalidInputError: If role name already exists
        """
        # Check if role exists
        existing = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        if existing.scalar_one_or_none():
            raise InvalidInputError(f"Role '{name}' already exists")
        
        # Create role
        role = Role(
            name=name,
            description=description,
            is_system_role=is_system_role
        )
        
        self.db.add(role)
        await self.db.commit()
        await self.db.refresh(role)
        
        # Assign permissions if provided
        if permission_ids:
            for permission_id in permission_ids:
                await self.assign_permission_to_role(role.id, permission_id)
        
        logger.info(f"Created role '{name}' with {len(permission_ids or [])} permissions")
        
        return role
    
    async def update_role(
        self,
        role_id: UUID,
        name: Optional[str] = None,
        description: Optional[str] = None
    ) -> Role:
        """
        Update role details.
        
        Args:
            role_id: Role ID
            name: New name (optional)
            description: New description (optional)
            
        Returns:
            Updated Role object
            
        Raises:
            ResourceNotFoundError: If role not found
            InvalidInputError: If new name already exists
        """
        role = await self.db.get(Role, role_id)
        if not role:
            raise ResourceNotFoundError(f"Role {role_id} not found")
        
        # Check if system role (shouldn't be modified)
        if role.is_system_role:
            logger.warning(f"Attempted to modify system role '{role.name}'")
            raise InvalidInputError("Cannot modify system roles")
        
        # Update fields
        if name and name != role.name:
            # Check name doesn't exist
            existing = await self.db.execute(
                select(Role).where(Role.name == name)
            )
            if existing.scalar_one_or_none():
                raise InvalidInputError(f"Role '{name}' already exists")
            role.name = name
        
        if description is not None:
            role.description = description
        
        await self.db.commit()
        await self.db.refresh(role)
        
        logger.info(f"Updated role {role_id}")
        
        return role
    
    async def delete_role(self, role_id: UUID) -> bool:
        """
        Delete role and all its assignments.
        
        Args:
            role_id: Role ID
            
        Returns:
            True if deleted, False if not found
            
        Raises:
            InvalidInputError: If attempting to delete system role
        """
        role = await self.db.get(Role, role_id)
        if not role:
            return False
        
        if role.is_system_role:
            raise InvalidInputError("Cannot delete system roles")
        
        # Delete role (cascade will handle role_permissions and user_roles)
        await self.db.delete(role)
        await self.db.commit()
        
        logger.info(f"Deleted role {role_id} ('{role.name}')")
        
        return True
    
    async def get_role_by_name(self, name: str) -> Optional[Role]:
        """Get role by name."""
        result = await self.db.execute(
            select(Role).where(Role.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all_roles(self, include_system: bool = True) -> List[Role]:
        """
        Get all roles.
        
        Args:
            include_system: Whether to include system roles
            
        Returns:
            List of Role objects
        """
        query = select(Role)
        
        if not include_system:
            query = query.where(Role.is_system_role == False)
        
        result = await self.db.execute(query)
        return list(result.scalars().all())
    
    # ============================================================
    # Permission Management
    # ============================================================
    
    async def create_permission(
        self,
        name: str,
        resource: str,
        action: str,
        description: Optional[str] = None
    ) -> Permission:
        """
        Create new permission.
        
        Args:
            name: Permission name (e.g., "contacts.view")
            resource: Resource type (e.g., "contacts")
            action: Action type (e.g., "view")
            description: Permission description
            
        Returns:
            Created Permission object
            
        Raises:
            InvalidInputError: If permission already exists
        """
        # Check if exists
        existing = await self.db.execute(
            select(Permission).where(Permission.name == name)
        )
        if existing.scalar_one_or_none():
            raise InvalidInputError(f"Permission '{name}' already exists")
        
        permission = Permission(
            name=name,
            resource=resource,
            action=action,
            description=description
        )
        
        self.db.add(permission)
        await self.db.commit()
        await self.db.refresh(permission)
        
        logger.info(f"Created permission '{name}'")
        
        return permission
    
    async def get_permission_by_name(self, name: str) -> Optional[Permission]:
        """Get permission by name."""
        result = await self.db.execute(
            select(Permission).where(Permission.name == name)
        )
        return result.scalar_one_or_none()
    
    async def get_all_permissions(self) -> List[Permission]:
        """Get all permissions."""
        result = await self.db.execute(select(Permission))
        return list(result.scalars().all())
    
    async def get_permissions_by_resource(self, resource: str) -> List[Permission]:
        """Get all permissions for a resource."""
        result = await self.db.execute(
            select(Permission).where(Permission.resource == resource)
        )
        return list(result.scalars().all())
    
    # ============================================================
    # Role-Permission Management
    # ============================================================
    
    async def assign_permission_to_role(
        self,
        role_id: UUID,
        permission_id: UUID
    ) -> RolePermission:
        """
        Assign permission to role.
        
        Args:
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            RolePermission object
            
        Raises:
            InvalidInputError: If role or permission doesn't exist
        """
        # Verify role exists
        role = await self.db.get(Role, role_id)
        if not role:
            raise InvalidInputError(f"Role {role_id} not found")
        
        # Verify permission exists
        permission = await self.db.get(Permission, permission_id)
        if not permission:
            raise InvalidInputError(f"Permission {permission_id} not found")
        
        # Check if already assigned
        existing = await self.db.execute(
            select(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
        )
        existing_rp = existing.scalar_one_or_none()
        
        if existing_rp:
            return existing_rp
        
        # Create assignment
        role_permission = RolePermission(
            role_id=role_id,
            permission_id=permission_id
        )
        
        self.db.add(role_permission)
        await self.db.commit()
        await self.db.refresh(role_permission)
        
        logger.info(
            f"Assigned permission '{permission.name}' to role '{role.name}'"
        )
        
        return role_permission
    
    async def revoke_permission_from_role(
        self,
        role_id: UUID,
        permission_id: UUID
    ) -> bool:
        """
        Revoke permission from role.
        
        Args:
            role_id: Role ID
            permission_id: Permission ID
            
        Returns:
            True if revoked, False if not found
        """
        result = await self.db.execute(
            delete(RolePermission).where(
                and_(
                    RolePermission.role_id == role_id,
                    RolePermission.permission_id == permission_id
                )
            )
        )
        
        await self.db.commit()
        
        return result.rowcount > 0
    
    async def get_role_permissions(self, role_id: UUID) -> List[Permission]:
        """
        Get all permissions for a role.
        
        Args:
            role_id: Role ID
            
        Returns:
            List of Permission objects
        """
        result = await self.db.execute(
            select(Permission)
            .join(RolePermission, RolePermission.permission_id == Permission.id)
            .where(RolePermission.role_id == role_id)
        )
        
        return list(result.scalars().all())
    
    async def set_role_permissions(
        self,
        role_id: UUID,
        permission_ids: List[UUID]
    ) -> None:
        """
        Set exact permissions for role (replaces existing).
        
        Args:
            role_id: Role ID
            permission_ids: List of permission IDs to set
        """
        # Verify role exists
        role = await self.db.get(Role, role_id)
        if not role:
            raise InvalidInputError(f"Role {role_id} not found")
        
        # Remove all existing permissions
        await self.db.execute(
            delete(RolePermission).where(RolePermission.role_id == role_id)
        )
        
        # Add new permissions
        for permission_id in permission_ids:
            role_permission = RolePermission(
                role_id=role_id,
                permission_id=permission_id
            )
            self.db.add(role_permission)
        
        await self.db.commit()
        
        logger.info(
            f"Set {len(permission_ids)} permissions for role '{role.name}'"
        )
    
    # ============================================================
    # Bulk Operations & Utilities
    # ============================================================
    
    async def get_users_with_permission(
        self,
        permission_name: str,
        agency_id: UUID
    ) -> List[AuthUser]:
        """
        Get all users who have a specific permission in an agency.
        
        Args:
            permission_name: Permission name
            agency_id: Agency ID
            
        Returns:
            List of AuthUser objects
        """
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            select(AuthUser)
            .join(UserRoleAssignment, UserRoleAssignment.user_id == AuthUser.id)
            .join(Role, Role.id == UserRoleAssignment.role_id)
            .join(RolePermission, RolePermission.role_id == Role.id)
            .join(Permission, Permission.id == RolePermission.permission_id)
            .where(
                and_(
                    Permission.name == permission_name,
                    UserRoleAssignment.agency_id == agency_id,
                    or_(
                        UserRoleAssignment.expires_at.is_(None),
                        UserRoleAssignment.expires_at > now
                    )
                )
            )
            .distinct()
        )
        
        return list(result.scalars().all())
    
    async def get_user_agencies(self, user_id: UUID) -> List[Agency]:
        """
        Get all agencies where user has any role.
        
        Args:
            user_id: User ID
            
        Returns:
            List of Agency objects
        """
        now = datetime.now(timezone.utc)
        
        result = await self.db.execute(
            select(Agency)
            .join(UserRoleAssignment, UserRoleAssignment.agency_id == Agency.id)
            .where(
                and_(
                    UserRoleAssignment.user_id == user_id,
                    or_(
                        UserRoleAssignment.expires_at.is_(None),
                        UserRoleAssignment.expires_at > now
                    )
                )
            )
            .distinct()
        )
        
        return list(result.scalars().all())

