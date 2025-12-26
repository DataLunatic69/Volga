"""
Lead Preferences model for storing lead property preferences.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, ARRAY, Numeric, Date
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel


class PropertyType(str):
    """Property type enum."""
    APARTMENT = "apartment"
    HOUSE = "house"
    STUDIO = "studio"
    COMMERCIAL = "commercial"


class TransactionType(str):
    """Transaction type enum."""
    RENT = "rent"
    BUY = "buy"


class Furnishing(str):
    """Furnishing enum."""
    FURNISHED = "furnished"
    UNFURNISHED = "unfurnished"
    EITHER = "either"


class Urgency(str):
    """Urgency enum."""
    IMMEDIATE = "immediate"
    WITHIN_MONTH = "within_month"
    WITHIN_3MONTHS = "within_3months"
    FLEXIBLE = "flexible"
    BROWSING = "browsing"


class LeadPreferences(BaseModel, table=True):
    """Lead Preferences table model."""
    __tablename__ = "lead_preferences"
    
    contact_id: UUID = Field(foreign_key="contacts.id", index=True)
    property_type: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: apartment, house, studio, commercial
    transaction_type: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: rent, buy
    budget_min: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    budget_max: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    budget_flexible: bool = Field(default=False, sa_column=Column(Boolean))
    bedrooms_min: Optional[int] = Field(default=None, sa_column=Column(Integer))
    bedrooms_max: Optional[int] = Field(default=None, sa_column=Column(Integer))
    bathrooms_min: Optional[int] = Field(default=None, sa_column=Column(Integer))
    bathrooms_max: Optional[int] = Field(default=None, sa_column=Column(Integer))
    preferred_locations: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    location_radius_km: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    furnishing: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: furnished, unfurnished, either
    move_in_date_earliest: Optional[date] = Field(default=None, sa_column=Column(Date))
    move_in_date_latest: Optional[date] = Field(default=None, sa_column=Column(Date))
    urgency: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: immediate, within_month, etc.
    must_have_features: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    nice_to_have_features: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    pets: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    additional_notes: Optional[str] = Field(default=None, sa_column=Column(Text))
