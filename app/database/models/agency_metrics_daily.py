"""
Agency Metrics Daily model for daily agency metrics.
"""
from datetime import date
from decimal import Decimal
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Integer, Numeric, Date
from sqlmodel import Field

from .base import BaseModel


class AgencyMetricsDaily(BaseModel, table=True):
    """Agency Metrics Daily table model."""
    __tablename__ = "agency_metrics_daily"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    metric_date: date = Field(sa_column=Column(Date), index=True)
    total_enquiries: int = Field(default=0, sa_column=Column(Integer))
    qualified_leads: int = Field(default=0, sa_column=Column(Integer))
    viewings_scheduled: int = Field(default=0, sa_column=Column(Integer))
    viewings_completed: int = Field(default=0, sa_column=Column(Integer))
    viewings_no_show: int = Field(default=0, sa_column=Column(Integer))
    applications_submitted: int = Field(default=0, sa_column=Column(Integer))
    deals_won: int = Field(default=0, sa_column=Column(Integer))
    deals_lost: int = Field(default=0, sa_column=Column(Integer))
    avg_response_time_seconds: Optional[int] = Field(default=None, sa_column=Column(Integer))
    avg_qualification_time_minutes: Optional[int] = Field(default=None, sa_column=Column(Integer))
    conversion_enquiry_to_qualified: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    conversion_qualified_to_viewing: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    conversion_viewing_to_application: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
    ai_handled_conversations: int = Field(default=0, sa_column=Column(Integer))
    escalated_conversations: int = Field(default=0, sa_column=Column(Integer))
    total_ai_cost_usd: Optional[Decimal] = Field(default=None, sa_column=Column(Numeric))
