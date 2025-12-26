"""
Conversation State Snapshots model for storing conversation state snapshots.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class CreatedBy(str):
    """Created by enum."""
    SYSTEM = "system"
    AGENT = "agent"
    SUPERVISOR = "supervisor"


class ConversationStateSnapshot(BaseModel, table=True):
    """Conversation State Snapshot table model."""
    __tablename__ = "conversation_state_snapshots"
    
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    state_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    state_data: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    created_by: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: system, agent, supervisor
    snapshot_at: Optional[datetime] = Field(default=None)
