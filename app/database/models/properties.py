"""
Properties model for real estate properties.
"""
from datetime import date, datetime
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
    PENTHOUSE = "penthouse"
    COMMERCIAL = "commercial"
    LAND = "land"


class TransactionType(str):
    """Transaction type enum."""
    RENT = "rent"
    BUY = "buy"


class PropertyStatus(str):
    """Property status enum."""
    AVAILABLE = "available"
    UNDER_OFFER = "under_offer"
    LET = "let"
    SOLD = "sold"
    WITHDRAWN = "withdrawn"


class PricePeriod(str):
    """Price period enum."""
    MONTH = "month"
    WEEK = "week"
    YEAR = "year"
    ONE_TIME = "one_time"


class Furnishing(str):
    """Furnishing enum."""
    FURNISHED = "furnished"
    UNFURNISHED = "unfurnished"
    SEMI_FURNISHED = "semi_furnished"


class Property(BaseModel, table=True):
    """Property table model."""
    __tablename__ = "properties"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    external_id: Optional[str] = Field(default=None, sa_column=Column(Text))
    title: Optional[str] = Field(default=None, sa_column=Column(Text))
    description: Optional[str] = Field(default=None, sa_column=Column(Text))
    property_type: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: apartment, house, studio, etc.
    transaction_type: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: rent, buy
    status: str = Field(default="available", sa_column=Column(Text))  # enum: available, under_offer, let, sold, withdrawn
    price: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    price_period: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: month, week, year, one_time
    bedrooms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    bathrooms: Optional[int] = Field(default=None, sa_column=Column(Integer))
    square_feet: Optional[int] = Field(default=None, sa_column=Column(Integer))
    square_meters: Optional[int] = Field(default=None, sa_column=Column(Integer))
    address: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    location_coordinates: Optional[str] = Field(default=None, sa_column=Column(Text))  # PostGIS geography(Point)
    area_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    furnishing: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: furnished, unfurnished, semi_furnished
    features: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    images: Optional[list[dict]] = Field(default=None, sa_column=SQLColumn(JSON))
    floor_plan_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    virtual_tour_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    epc_rating: Optional[str] = Field(default=None, sa_column=Column(Text))
    council_tax_band: Optional[str] = Field(default=None, sa_column=Column(Text))
    available_from: Optional[date] = Field(default=None, sa_column=Column(Date))
    available_until: Optional[date] = Field(default=None, sa_column=Column(Date))
    listing_url: Optional[str] = Field(default=None, sa_column=Column(Text))
    portal_links: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    assigned_agent_id: Optional[UUID] = Field(default=None, foreign_key="agency_users.id")
    viewing_duration_minutes: int = Field(default=30, sa_column=Column(Integer))
    is_featured: bool = Field(default=False, sa_column=Column(Boolean))
    view_count: int = Field(default=0, sa_column=Column(Integer))
    interest_count: int = Field(default=0, sa_column=Column(Integer))
    embedding_vector: Optional[str] = Field(default=None, sa_column=Column(Text))  # Qdrant ID reference
    last_synced_at: Optional[datetime] = Field(default=None)
