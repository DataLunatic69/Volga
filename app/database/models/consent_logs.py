"""
Consent Logs model for tracking consent records.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean
from sqlalchemy.dialects.postgresql import INET
from sqlmodel import Field

from .base import BaseModel


class ConsentType(str):
    """Consent type enum."""
    DATA_PROCESSING = "data_processing"
    MARKETING = "marketing"
    THIRD_PARTY_SHARING = "third_party_sharing"


class ConsentMethod(str):
    """Consent method enum."""
    WHATSAPP_CHAT = "whatsapp_chat"
    VOICE_CALL = "voice_call"
    WEB_FORM = "web_form"
    IN_PERSON = "in_person"


class ConsentLog(BaseModel, table=True):
    """Consent Log table model."""
    __tablename__ = "consent_logs"
    
    contact_id: UUID = Field(foreign_key="contacts.id", index=True)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    consent_type: str = Field(sa_column=Column(Text))  # enum: data_processing, marketing, third_party_sharing
    consent_status: bool = Field(sa_column=Column(Boolean))
    consent_method: str = Field(sa_column=Column(Text))  # enum: whatsapp_chat, voice_call, etc.
    consent_language: Optional[str] = Field(default=None, sa_column=Column(Text))
    consent_response: Optional[str] = Field(default=None, sa_column=Column(Text))
    ip_address: Optional[str] = Field(default=None, sa_column=Column(INET))
    user_agent: Optional[str] = Field(default=None, sa_column=Column(Text))
    conversation_id: Optional[UUID] = Field(default=None, foreign_key="conversations.id")
    message_id: Optional[UUID] = Field(default=None, foreign_key="messages.id")
    withdrawn_at: Optional[datetime] = Field(default=None)
