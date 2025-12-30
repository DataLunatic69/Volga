"""
Password Reset Tokens model - For password reset functionality.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, DateTime
from sqlmodel import Field

from .base import BaseModel


class PasswordResetToken(BaseModel, table=True):
    """Password reset token table."""
    __tablename__ = "password_reset_tokens"
    
    user_id: UUID = Field(foreign_key="auth_users.id", index=True)
    token_hash: str = Field(sa_column=Column(Text))
    expires_at: datetime = Field(sa_column=Column(DateTime(timezone=True)))
    used_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )

