"""
Refresh Tokens model - Secure refresh token management.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import Column, Text, DateTime, Boolean, String, ForeignKey
from sqlalchemy.dialects.postgresql import JSONB, UUID as PGUUID
from sqlmodel import Field

from .base import BaseModel


class RefreshToken(BaseModel, table=True):
    """Refresh token table for secure token rotation."""
    __tablename__ = "refresh_tokens"
    
    user_id: PyUUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), ForeignKey("auth_users.id", ondelete="CASCADE"), index=True)
    )
    token_hash: str = Field(sa_column=Column(Text))  # SHA-256 hashed token
    token_prefix: Optional[str] = Field(
        default=None,
        sa_column=Column(String(8), index=True, nullable=True)  # First 8 chars for O(1) lookup
    )
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

