"""
Roles model - User roles for RBAC.
"""
from typing import Optional

from sqlalchemy import Column, Text, Boolean
from sqlmodel import Field

from .base import BaseModel


class Role(BaseModel, table=True):
    """Role table for role-based access control."""
    __tablename__ = "roles"
    
    name: str = Field(
        unique=True,
        index=True,
        sa_column=Column(Text)
    )  # "super_admin", "agency_admin", "agent", "manager", "viewer"
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_system_role: bool = Field(
        default=False,
        sa_column=Column(Boolean)
    )  # true for built-in roles

