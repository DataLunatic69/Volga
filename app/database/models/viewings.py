"""
Viewings model for property viewings.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field

from .base import BaseModel


class ViewingType(str):
    """Viewing type enum."""
    IN_PERSON = "in_person"
    VIRTUAL = "virtual"
    OPEN_HOUSE = "open_house"


class ViewingStatus(str):
    """Viewing status enum."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    NO_SHOW = "no_show"
    RESCHEDULED = "rescheduled"


class CancelledBy(str):
    """Cancelled by enum."""
    CONTACT = "contact"
    AGENT = "agent"
    SYSTEM = "system"


class Viewing(BaseModel, table=True):
    """Viewing table model."""
    __tablename__ = "viewings"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    contact_id: UUID = Field(foreign_key="contacts.id", index=True)
    property_id: UUID = Field(foreign_key="properties.id", index=True)
    agent_id: UUID = Field(foreign_key="agency_users.id", index=True)
    conversation_id: Optional[UUID] = Field(default=None, foreign_key="conversations.id")
    viewing_type: str = Field(sa_column=Column(Text))  # enum: in_person, virtual, open_house
    status: str = Field(default="scheduled", sa_column=Column(Text))  # enum: scheduled, confirmed, completed, etc.
    scheduled_start: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))
    scheduled_end: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))
    actual_start: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    actual_end: Optional[datetime] = Field(default=None, sa_column=Column(TIMESTAMP(timezone=True)))
    meeting_location: Optional[str] = Field(default=None, sa_column=Column(Text))
    meeting_instructions: Optional[str] = Field(default=None, sa_column=Column(Text))
    calendar_event_id: Optional[str] = Field(default=None, sa_column=Column(Text))
    confirmation_sent_at: Optional[datetime] = Field(default=None)
    reminder_24h_sent_at: Optional[datetime] = Field(default=None)
    reminder_2h_sent_at: Optional[datetime] = Field(default=None)
    cancellation_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    cancelled_by: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: contact, agent, system
    cancelled_at: Optional[datetime] = Field(default=None)
    rescheduled_from_viewing_id: Optional[UUID] = Field(default=None, foreign_key="viewings.id")
    feedback_requested_at: Optional[datetime] = Field(default=None)
    feedback_received_at: Optional[datetime] = Field(default=None)
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
