"""
Base model for all database tables using SQLModel.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import Column, DateTime, func
from sqlmodel import Field, SQLModel


class TimestampMixin:
    """Mixin for created_at and updated_at timestamps."""
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_column=Column(DateTime(timezone=True), server_default=func.now())
    )
    updated_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True), onupdate=func.now())
    )


class BaseModel(SQLModel, TimestampMixin, table=False):
    """Base model with UUID primary key and timestamps."""
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )