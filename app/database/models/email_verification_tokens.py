"""
Email Verification Tokens model - For email verification functionality.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, DateTime
from sqlmodel import Field

from .base import BaseModel


class EmailVerificationToken(BaseModel, table=True):
    """Email verification token table."""
    __tablename__ = "email_verification_tokens"
    
    user_id: UUID = Field(foreign_key="auth_users.id", index=True)
    token_hash: str = Field(sa_column=Column(Text))
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    verified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

