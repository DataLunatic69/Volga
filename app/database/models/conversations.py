"""
Conversations model for chat conversations.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Numeric
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class Channel(str):
    """Channel enum."""
    WHATSAPP = "whatsapp"
    VOICE = "voice"
    SMS = "sms"
    WEB_CHAT = "web_chat"


class ConversationStatus(str):
    """Conversation status enum."""
    ACTIVE = "active"
    PAUSED = "paused"
    CLOSED = "closed"
    ESCALATED = "escalated"
    ABANDONED = "abandoned"


class CurrentStage(str):
    """Current stage enum."""
    GREETING = "greeting"
    CONSENT = "consent"
    QUALIFICATION = "qualification"
    PROPERTY_MATCHING = "property_matching"
    BOOKING = "booking"
    FOLLOW_UP = "follow_up"
    COMPLETED = "completed"


class Conversation(BaseModel, table=True):
    """Conversation table model."""
    __tablename__ = "conversations"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    contact_id: UUID = Field(foreign_key="contacts.id", index=True)
    channel: str = Field(sa_column=Column(Text))  # enum: whatsapp, voice, sms, web_chat
    conversation_status: str = Field(default="active", sa_column=Column(Text))  # enum: active, paused, closed, etc.
    current_stage: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: greeting, consent, etc.
    session_data: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    assigned_agent_id: Optional[UUID] = Field(default=None, foreign_key="agency_users.id")
    escalation_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    escalated_at: Optional[datetime] = Field(default=None)
    ai_confidence_score: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    sentiment_score: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))  # -1 to 1
    language_detected: Optional[str] = Field(default=None, sa_column=Column(Text))
    started_at: Optional[datetime] = Field(default=None)
    ended_at: Optional[datetime] = Field(default=None)
