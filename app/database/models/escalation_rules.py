"""
Escalation Rules model for escalation rule configurations.
"""
from typing import Optional
from uuid import UUID

from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer
from sqlmodel import Field, JSON, Column as SQLColumn

from .base import BaseModel

from .base import BaseModel


class EscalationRule(BaseModel, table=True):
    """Escalation Rule table model."""
    __tablename__ = "escalation_rules"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    rule_name: Optional[str] = Field(default=None, sa_column=Column(Text))
    rule_conditions: Optional[dict] = Field(default=None, sa_column=SQLColumn(JSON))
    escalation_action: Optional[str] = Field(default=None, sa_column=Column(Text))
    is_active: bool = Field(default=True, sa_column=Column(Boolean))
    priority: Optional[int] = Field(default=None, sa_column=Column(Integer))

