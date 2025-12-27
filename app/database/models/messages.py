"""
Messages model for conversation messages.
"""
from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Integer, ARRAY, Numeric
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class Direction(str):
    """Direction enum."""
    INBOUND = "inbound"
    OUTBOUND = "outbound"


class SenderType(str):
    """Sender type enum."""
    CONTACT = "contact"
    AI_AGENT = "ai_agent"
    HUMAN_AGENT = "human_agent"


class MessageType(str):
    """Message type enum."""
    TEXT = "text"
    IMAGE = "image"
    DOCUMENT = "document"
    AUDIO = "audio"
    VIDEO = "video"
    LOCATION = "location"
    TEMPLATE = "template"


class Message(BaseModel, table=True):
    """Message table model."""
    __tablename__ = "messages"
    
    conversation_id: UUID = Field(foreign_key="conversations.id", index=True)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    contact_id: UUID = Field(foreign_key="leads.id", index=True)
    direction: str = Field(sa_column=Column(Text))  # enum: inbound, outbound
    sender_type: str = Field(sa_column=Column(Text))  # enum: contact, ai_agent, human_agent
    sender_id: Optional[UUID] = Field(default=None)  # if human_agent, FK to agency_users
    message_type: str = Field(sa_column=Column(Text))  # enum: text, image, document, etc.
    content: Optional[str] = Field(default=None, sa_column=Column(Text))
    media_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    message_metadata: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    agent_type: Optional[str] = Field(default=None, sa_column=Column(Text))
    tool_calls: Optional[list[dict]] = Field(default=None, sa_column=SQLColumn(JSON))
    processing_time_ms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    llm_model_used: Optional[str] = Field(default=None, sa_column=Column(Text))
    tokens_used: Optional[int] = Field(default=None, sa_column=Column(Integer))
    cost_usd: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    read_at: Optional[datetime] = Field(default=None)
    delivered_at: Optional[datetime] = Field(default=None)
