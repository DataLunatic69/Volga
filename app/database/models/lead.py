"""
Lead model for potential customers.
"""
from datetime import datetime
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, ARRAY, JSON as SA_JSON
from sqlalchemy.dialects.postgresql import INET
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class ContactSource(str):
    """Contact source enum."""
    WHATSAPP = "whatsapp"
    PHONE = "phone"
    WEBSITE = "website"
    PORTAL = "portal"
    REFERRAL = "referral"
    WALK_IN = "walk_in"


class LifecycleStage(str):
    """Lifecycle stage enum."""
    NEW = "new"
    CONTACTED = "contacted"
    QUALIFIED = "qualified"
    VIEWING_SCHEDULED = "viewing_scheduled"
    VIEWING_COMPLETED = "viewing_completed"
    APPLICATION_SUBMITTED = "application_submitted"
    OFFER_MADE = "offer_made"
    CONVERTED = "converted"
    LOST = "lost"
    NURTURE = "nurture"


class Lead(BaseModel, table=True):
    """Lead table model."""
    __tablename__ = "leads"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    whatsapp_number: Optional[str] = Field(default=None, sa_column=Column(Text, index=True))
    email: Optional[str] = Field(default=None, sa_column=Column(Text))
    full_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    preferred_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    language: str = Field(default="en", sa_column=Column(Text))
    contact_source: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: whatsapp, phone, website, portal, referral, walk_in
    lifecycle_stage: str = Field(default="new", sa_column=Column(Text))  # enum: new, contacted, qualified, etc.
    lead_score: Optional[int] = Field(default=None, sa_column=Column(Integer))  # 0-100
    consent_given: bool = Field(default=False, sa_column=Column(Boolean))
    consent_timestamp: Optional[datetime] = Field(default=None)
    consent_ip_address: Optional[str] = Field(default=None, sa_column=Column(INET))
    consent_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    data_processing_consent: bool = Field(default=False, sa_column=Column(Boolean))
    marketing_consent: bool = Field(default=False, sa_column=Column(Boolean))
    tags: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    custom_fields: Optional[dict] = Field(default=None, sa_column=SQLColumn(SA_JSON))
    last_interaction_at: Optional[datetime] = Field(default=None)
