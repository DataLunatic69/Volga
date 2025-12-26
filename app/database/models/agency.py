"""
Agency model for real estate agencies.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class BusinessType(str):
    """Business type enum."""
    RESIDENTIAL_SALES = "residential_sales"
    RESIDENTIAL_RENTALS = "residential_rentals"
    COMMERCIAL = "commercial"
    MIXED = "mixed"


class SubscriptionTier(str):
    """Subscription tier enum."""
    STARTER = "starter"
    PROFESSIONAL = "professional"
    ENTERPRISE = "enterprise"


class SubscriptionStatus(str):
    """Subscription status enum."""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    TRIAL = "trial"
    CANCELLED = "cancelled"


class Agency(BaseModel, table=True):
    """Agency table model."""
    __tablename__ = "agencies"
    
    name: str = Field(sa_column=Column(Text))
    slug: str = Field(sa_column=Column(Text, unique=True, index=True))
    business_type: str = Field(sa_column=Column(Text))  # enum: residential_sales, residential_rentals, commercial, mixed
    email: Optional[str] = Field(default=None, sa_column=Column(Text))
    phone: Optional[str] = Field(default=None, sa_column=Column(Text))
    address: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    logo_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    branding_config: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    whatsapp_business_account_id: Optional[str] = Field(default=None, sa_column=Column(Text))
    whatsapp_phone_number: Optional[str] = Field(default=None, sa_column=Column(Text))
    subscription_tier: str = Field(default="starter", sa_column=Column(Text))  # enum: starter, professional, enterprise
    subscription_status: str = Field(default="trial", sa_column=Column(Text))  # enum: active, suspended, trial, cancelled
    ai_config: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    timezone: Optional[str] = Field(default=None, sa_column=Column(Text))
    business_hours: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
