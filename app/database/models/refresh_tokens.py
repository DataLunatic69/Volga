"""
Refresh Tokens model - Secure refresh token management.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, DateTime, Boolean
from sqlalchemy.dialects.postgresql import JSONB
from sqlmodel import Field

from .base import BaseModel


class RefreshToken(BaseModel, table=True):
    """Refresh token table for secure token rotation."""
    __tablename__ = "refresh_tokens"
    
    user_id: UUID = Field(foreign_key="auth_users.id", index=True)
    token_hash: str = Field(sa_column=Column(Text))  # hashed refresh token
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    revoked_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    device_info: Optional[dict] = Field(
        default=None,
        sa_column=Column(JSONB)  # user agent, IP
    )
    is_revoked: bool = Field(default=False, sa_column=Column(Boolean))

