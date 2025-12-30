"""
Auth Users model - Core authentication table.
Decouples authentication from business logic.
"""
from datetime import datetime, timezone
from typing import Optional
from uuid import UUID

from sqlalchemy import Column, Text, Boolean, Integer, DateTime
from sqlmodel import Field

from .base import BaseModel


class AuthUser(BaseModel, table=True):
    """Core authentication user table."""
    __tablename__ = "auth_users"
    
    email: str = Field(unique=True, index=True, sa_column=Column(Text))
    password_hash: str = Field(sa_column=Column(Text))  # bcrypt hashed
    is_active: bool = Field(default=True, sa_column=Column(Boolean))
    is_verified: bool = Field(default=False, sa_column=Column(Boolean))
    email_verified_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    last_login_at: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))
    )
    failed_login_attempts: int = Field(default=0, sa_column=Column(Integer))
    locked_until: Optional[datetime] = Field(
        default=None,
        sa_column=Column(DateTime(timezone=True))  # for account lockout
    )

