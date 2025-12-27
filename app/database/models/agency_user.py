"""
Agency User model for users within an agency.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class UserRole(str):
    """User role enum."""
    ADMIN = "admin"
    AGENT = "agent"
    MANAGER = "manager"
    VIEWER = "viewer"


class AgencyUser(BaseModel, table=True):
    """Agency User table model."""
    __tablename__ = "agency_users"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    user_id: UUID = Field(index=True)
    role: str = Field(default="agent", sa_column=Column(Text))  # enum: admin, agent, manager, viewer
    full_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    email: Optional[str] = Field(default=None, sa_column=Column(Text))
    phone: Optional[str] = Field(default=None, sa_column=Column(Text))
    avatar_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True, sa_column=Column(Boolean))
    calendar_integration: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    working_hours: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    max_viewings_per_day: Optional[int] = Field(default=None)
    notification_preferences: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
