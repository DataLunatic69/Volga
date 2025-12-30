"""
Permissions model - Fine-grained permissions for RBAC.
"""
from typing import Optional

from sqlalchemy import Column, Text
from sqlmodel import Field

from .base import BaseModel


class Permission(BaseModel, table=True):
    """Permission table for fine-grained access control."""
    __tablename__ = "permissions"
    
    name: str = Field(
        unique=True,
        index=True,
        sa_column=Column(Text)
    )  # "contacts.view", "contacts.edit", "properties.delete"
    resource: str = Field(
        index=True,
        sa_column=Column(Text)
    )  # "contacts", "properties", "viewings"
    action: str = Field(
        index=True,
        sa_column=Column(Text)
    )  # "view", "edit", "create", "delete"
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

