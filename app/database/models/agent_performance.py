"""
Agent Performance model for tracking agent performance metrics.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Integer, Numeric, Date
from sqlmodel import Field

from .base import BaseModel


class AgentPerformance(BaseModel, table=True):
    """Agent Performance table model."""
    __tablename__ = "agent_performance"
    
    agent_id: UUID = Field(foreign_key="agency_users.id", index=True)
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    metric_date: date = Field(sa_column=Column(Date), index=True)
    viewings_conducted: int = Field(default=0, sa_column=Column(Integer))
    viewings_completed_on_time: int = Field(default=0, sa_column=Column(Integer))
    viewings_cancelled: int = Field(default=0, sa_column=Column(Integer))
    applications_received: int = Field(default=0, sa_column=Column(Integer))
    deals_closed: int = Field(default=0, sa_column=Column(Integer))
    avg_viewing_duration_minutes: Optional[int] = Field(default=None, sa_column=Column(Integer))
    avg_response_time_minutes: Optional[int] = Field(default=None, sa_column=Column(Integer))
    commission_earned: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
