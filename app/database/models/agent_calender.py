"""
Agent Calendar model for agent calendar configurations.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean
from sqlmodel import Field

from .base import BaseModel


class AgentCalendar(BaseModel, table=True):
    """Agent Calendar table model."""
    __tablename__ = "agent_calendars"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    agent_id: UUID = Field(foreign_key="agency_users.id", index=True)
    calendar_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    timezone: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_default: bool = Field(default=False, sa_column=Column(Boolean))
    color: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True, sa_column=Column(Boolean))
