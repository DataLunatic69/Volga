"""
API Keys model - For integrations and API access.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, DateTime, ARRAY
from sqlmodel import Field

from .base import BaseModel


class APIKey(BaseModel, table=True):
    """API Key table for integrations and API access."""
    __tablename__ = "api_keys"
    
    agency_id: UUID = Field(foreign_key="agencies.id", index=True)
    key_hash: str = Field(sa_column=Column(Text))  # bcrypt hashed
    key_prefix: str = Field(
        sa_column=Column(Text, index=True)
    )  # "nexc_live_abc..." for identification
    name: str = Field(sa_column=Column(Text))  # "Production API Key"
    scopes: list[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(Text))
    )  # ["contacts.read", "viewings.write"]
    last_used_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    expires_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    is_active: bool = Field(default=True, sa_column=Column(Boolean))
    created_by: UUID = Field(foreign_key="auth_users.id")

