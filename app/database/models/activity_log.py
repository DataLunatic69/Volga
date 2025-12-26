"""
Activity Log model for tracking system activities.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy.dialects.postgresql import INET
from sqlalchemy import Text, Column
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class ActorType(str):
    """Actor type enum."""
    CONTACT = "contact"
    AI_AGENT = "ai_agent"
    HUMAN_AGENT = "human_agent"
    SYSTEM = "system"


class Severity(str):
    """Severity enum."""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class ActivityLog(BaseModel, table=True):
    """Activity Log table model."""
    __tablename__ = "activity_logs"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    actor_type: str = Field(sa_column=Column(Text))  # enum: contact, ai_agent, human_agent, system
    actor_id: Optional[UUID] = Field(default=None)
    action_type: Optional[str] = Field(default=None, sa_column=Column(Text))
    resource_type: Optional[str] = Field(default=None, sa_column=Column(Text))
    resource_id: Optional[UUID] = Field(default=None)
    details: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    log_metadata: Optional[dict] = Field(default=None, sa_column=Column(JSON))
    severity: str = Field(default="info", sa_column=Column(Text))  # enum: info, warning, error, critical
    ip_address: Optional[str] = Field(default=None, sa_column=Column(INET))
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
