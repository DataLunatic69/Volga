"""
User Roles model - Many-to-many relationship between users and roles, scoped to agencies.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, DateTime
from sqlmodel import Field

from .base import BaseModel


class UserRole(BaseModel, table=True):
    """
    Many-to-many relationship between users and roles, scoped to agencies.
    
    A user can be:
    - Admin in Agency A
    - Agent in Agency B
    - Viewer in Agency C
    """
    __tablename__ = "user_roles"
    
    user_id: UUID = Field(foreign_key="auth_users.id", index=True)
    role_id: UUID = Field(foreign_key="roles.id", index=True)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)  # Role is scoped to agency
    granted_by: UUID = Field(foreign_key="auth_users.id")  # Who granted this role
    granted_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True))
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))  # optional, for temporary access
    )

