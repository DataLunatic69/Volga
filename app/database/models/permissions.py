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
        sa_column=Column(Text, unique=True, index=True)
    )  # "contacts.view", "contacts.edit", "properties.delete"
    resource: str = Field(
        sa_column=Column(Text, index=True)
    )  # "contacts", "properties", "viewings"
    action: str = Field(
        sa_column=Column(Text, index=True)
    )  # "view", "edit", "create", "delete"
    description: Optional[str] = Field(default=None, sa_column=Column(Text))

