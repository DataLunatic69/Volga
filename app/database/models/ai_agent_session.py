"""
AI Agent Session model for tracking AI agent sessions.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, ARRAY, Numeric
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class AIAgentSession(BaseModel, table=True):
    """AI Agent Session table model."""
    __tablename__ = "ai_agent_sessions"
    
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    agent_type: Optional[str] = Field(default=None, sa_column=Column(Text))  # "SupervisorAgent", "QualificationAgent"
    graph_state: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    total_tokens_used: Optional[int] = Field(default=None, sa_column=Column(Integer))
    total_cost_usd: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    tools_called: Optional[list[dict]] = Field(default=None, sa_column=SQLColumn(JSON))
    errors_encountered: Optional[list[dict]] = Field(default=None, sa_column=SQLColumn(JSON))
    escalated: bool = Field(default=False, sa_column=Column(Boolean))
    escalation_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
