"""
Password Reset Tokens model - For password reset functionality.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID as PyUUID

from sqlalchemy import Column, Text, DateTime, String, ForeignKey
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlmodel import Field

from .base import BaseModel


class PasswordResetToken(BaseModel, table=True):
    """Password reset token table."""
    __tablename__ = "password_reset_tokens"
    
    user_id: PyUUID = Field(
        sa_column=Column(PGUUID(as_uuid=True), ForeignKey("auth_users.id", ondelete="CASCADE"), index=True)
    )
    token_hash: str = Field(sa_column=Column(Text))  # SHA-256 hashed token
    token_prefix: Optional[str] = Field(
        default=None,
        sa_column=Column(String(8), index=True, nullable=True)  # First 8 chars for O(1) lookup
    )
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    used_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

