"""
Property Availability model for property availability schedules.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Time, Boolean, Integer
from sqlmodel import Field

from .base import BaseModel


class PropertyAvailability(BaseModel, table=True):
    """Property Availability table model."""
    __tablename__ = "property_availability"
    
    property_id: UUID = Field(foreign_key="properties.id", index=True)
    agent_id: UUID = Field(foreign_key="agency_users.id", index=True)
    day_of_week: int = Field(sa_column=Column(Integer))  # 0-6
    available_from_time: Optional[str] = Field(default=None, sa_column=Column(Time))
    available_to_time: Optional[str] = Field(default=None, sa_column=Column(Time))
    is_available: bool = Field(default=True, sa_column=Column(Boolean))
