"""
Deals model for tracking deals and sales pipeline.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from datetime import datetime
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Numeric, Date, Integer
from sqlmodel import Field

from .base import BaseModel


class DealStage(str):
    """Deal stage enum."""
    LEAD = "lead"
    QUALIFIED = "qualified"
    VIEWING_SCHEDULED = "viewing_scheduled"
    VIEWING_COMPLETED = "viewing_completed"
    APPLICATION_SUBMITTED = "application_submitted"
    REFERENCING = "referencing"
    OFFER_MADE = "offer_made"
    OFFER_ACCEPTED = "offer_accepted"
    CONTRACTS_SIGNED = "contracts_signed"
    COMPLETED = "completed"
    LOST = "lost"


class Deal(BaseModel, table=True):
    """Deal table model."""
    __tablename__ = "deals"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    contact_id: UUID = Field(foreign_key="leads.id", index=True)
    property_id: UUID = Field(foreign_key="properties.id", index=True)
    deal_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    deal_stage: str = Field(default="lead", sa_column=Column(Text))  # enum: lead, qualified, etc.
    deal_value: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    probability: Optional[int] = Field(default=None, sa_column=Column(Integer))  # 0-100
    expected_close_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    owner_agent_id: Optional[UUID] = Field(default=None, foreign_key="agency_users.id")
    lost_reason: Optional[str] = Field(default=None, sa_column=Column(Text))
    lost_at: Optional[datetime] = Field(default=None)
    won_at: Optional[datetime] = Field(default=None)
    close_date: Optional[date] = Field(default=None, sa_column=Column(Date))
    commission_amount: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    notes: Optional[str] = Field(default=None, sa_column=Column(Text))
