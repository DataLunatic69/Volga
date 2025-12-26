"""
Calendar Events model for calendar events and appointments.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, ARRAY
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlmodel import Field

from .base import BaseModel


class EventType(str):
    """Event type enum."""
    VIEWING = "viewing"
    BLOCK = "block"
    MEETING = "meeting"
    PERSONAL = "personal"
    HOLIDAY = "holiday"
    TRAINING = "training"


class EventStatus(str):
    """Event status enum."""
    SCHEDULED = "scheduled"
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    TENTATIVE = "tentative"
    NO_SHOW = "no_show"


class CalendarEvent(BaseModel, table=True):
    """Calendar Event table model."""
    __tablename__ = "calendar_events"
    
    calendar_id: UUID = Field(foreign_key="agent_calendars.id", index=True)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    agent_id: UUID = Field(foreign_key="agency_users.id", index=True)
    event_type: str = Field(sa_column=Column(Text))  # enum: viewing, block, meeting, personal, holiday, training
    title: Optional[str] = Field(default=None, sa_column=Column(Text))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    location: Optional[str] = Field(default=None, sa_column=Column(Text))
    start_time: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))
    end_time: datetime = Field(sa_column=Column(TIMESTAMP(timezone=True)))
    all_day: bool = Field(default=False, sa_column=Column(Boolean))
    timezone: Optional[str] = Field(default=None, sa_column=Column(Text))
    status: str = Field(default="scheduled", sa_column=Column(Text))  # enum: scheduled, confirmed, completed, etc.
    viewing_id: Optional[UUID] = Field(default=None, foreign_key="viewings.id")
    contact_id: Optional[UUID] = Field(default=None, foreign_key="contacts.id")
    property_id: Optional[UUID] = Field(default=None, foreign_key="properties.id")
    is_recurring: bool = Field(default=False, sa_column=Column(Boolean))
    recurrence_rule: Optional[str] = Field(default=None, sa_column=Column(Text))  # RRULE format
    recurrence_parent_id: Optional[UUID] = Field(default=None, foreign_key="calendar_events.id")
    reminder_minutes_before: Optional[list[int]] = Field(default=None, sa_column=Column(ARRAY(Integer)))
    created_by: UUID = Field(foreign_key="agency_users.id")
    color: Optional[str] = Field(default=None, sa_column=Column(Text))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_visible_to_client: bool = Field(default=True, sa_column=Column(Boolean))
    cancelled_at: Optional[datetime] = Field(default=None)
    cancelled_by: Optional[UUID] = Field(default=None, foreign_key="agency_users.id")
    cancellation_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
