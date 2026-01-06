"""
Base model for all database tables using SQLModel.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID, uuid4

from sqlalchemy import DateTime
from sqlmodel import Field, SQLModel


class BaseModel(SQLModel, table=False):
    """Base model with UUID primary key and timestamps."""
    id: UUID = Field(
        default_factory=uuid4,
        primary_key=True,
        index=True
    )
    
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        sa_type=DateTime(timezone=True),
    )

    updated_at: Optional[datetime] = Field(
        default=None,
        sa_type=DateTime(timezone=True),
    )