"""
Role Permissions model - Many-to-many relationship between roles and permissions.
"""
from uuid import UUID

from sqlalchemy import Column, UniqueConstraint
from sqlmodel import Field

from .base import BaseModel


class RolePermission(BaseModel, table=True):
    """Many-to-many relationship between roles and permissions."""
    __tablename__ = "role_permissions"
    
    role_id: UUID = Field(foreign_key="roles.id", index=True)
    permission_id: UUID = Field(foreign_key="permissions.id", index=True)
    
    # Ensure unique combination of role_id and permission_id
    __table_args__ = (
        UniqueConstraint("role_id", "permission_id", name="uq_role_permission"),
    )

