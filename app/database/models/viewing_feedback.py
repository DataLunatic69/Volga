"""
Viewing Feedback model for feedback on property viewings.
"""
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, ARRAY
from sqlmodel import Field

from .base import BaseModel


class CollectedBy(str):
    """Collected by enum."""
    AI = "ai"
    AGENT = "agent"
    FORM = "form"


class ViewingFeedback(BaseModel, table=True):
    """Viewing Feedback table model."""
    __tablename__ = "viewing_feedback"
    
    viewing_id: UUID = Field(foreign_key="viewings.id", index=True)
    contact_id: UUID = Field(foreign_key="leads.id", index=True)
    overall_rating: Optional[int] = Field(default=None, sa_column=Column(Integer))  # 1-5
    liked_aspects: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    disliked_aspects: Optional[list[str]] = Field(default=None, sa_column=Column(ARRAY(Text)))
    interested_in_applying: bool = Field(default=False, sa_column=Column(Boolean))
    wants_to_see_more: bool = Field(default=False, sa_column=Column(Boolean))
    additional_requirements: Optional[str] = Field(default=None, sa_column=Column(Text))
    feedback_text: Optional[str] = Field(default=None, sa_column=Column(Text))
    collected_by: Optional[str] = Field(default=None, sa_column=Column(Text))  # enum: ai, agent, form
