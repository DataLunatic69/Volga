"""
Authentication service for user registration, login, token management, etc.
"""
from datetime import datetime, timedelta, timezone
from typing import Optional, Dict, Any
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.models import (
    AuthUser,
    RefreshToken,
    EmailVerificationToken,
    PasswordResetToken,
    AgencyUser,
    Agency,
)
from app.auth.password import hash_password, verify_password, check_password_strength
from app.auth.jwt import create_access_token, create_refresh_token, verify_token
from app.auth.cache import AuthCache
from app.auth.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserAlreadyExistsError,
    UserInactiveError,
    UserNotVerifiedError,
    AccountLockedError,
    TokenExpiredError,
    InvalidTokenError,
    RefreshTokenRevokedError,
)


class AuthService:
    """Service for authentication operations."""
    
    # Account lockout settings
    MAX_FAILED_ATTEMPTS = 5
    LOCKOUT_DURATION_MINUTES = 30
    
    # Token expiration settings
    REFRESH_TOKEN_EXPIRE_DAYS = 30
    EMAIL_VERIFICATION_EXPIRE_HOURS = 24
    PASSWORD_RESET_EXPIRE_HOURS = 1
    
    def __init__(self, db: AsyncSession):
        """
        Initialize auth service.
        
        Args:
            db: Database session
        """
        self.db = db
    
    async def register(
        self,
        email: str,
        password: str,
        full_name: Optional[str] = None
    ) -> tuple[AuthUser, str, str]:
        """
        Register a new user.
        
        Args:
            email: User email
            password: Plain text password
            full_name: Optional full name
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            UserAlreadyExistsError: If user already exists
            ValueError: If password doesn't meet requirements
        """
        # Check if user already exists
        existing_user = await self.db.execute(
            select(AuthUser).where(AuthUser.email == email.lower())
        )
        if existing_user.scalar_one_or_none():
            raise UserAlreadyExistsError(f"User with email {email} already exists")
        
        # Validate password strength
        is_valid, error_msg = check_password_strength(password)
        if not is_valid:
            raise ValueError(error_msg or "Password does not meet requirements")
        
        # Hash password
        password_hash = hash_password(password)
        
        # Create user
        user = AuthUser(
            email=email.lower(),
            password_hash=password_hash,
            is_active=True,
            is_verified=False,  # Email verification required
            failed_login_attempts=0
        )
        
        self.db.add(user)
        await self.db.commit()
        await self.db.refresh(user)
        
        # Cache user
        await AuthCache.set_user(user)
        
        # Generate tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email
        )
        
        plain_refresh_token = create_refresh_token()
        refresh_token_hash = hash_password(plain_refresh_token)  # Hash for storage
        
        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            device_info=None
        )
        self.db.add(refresh_token)
        await self.db.commit()
        
        return user, access_token, plain_refresh_token
    
    async def login(
        self,
        email: str,
        password: str,
        device_info: Optional[Dict[str, Any]] = None
    ) -> tuple[AuthUser, str, str]:
        """
        Authenticate user and generate tokens.
        
        Args:
            email: User email
            password: Plain text password
            device_info: Optional device information (user agent, IP, etc.)
            
        Returns:
            Tuple of (user, access_token, refresh_token)
            
        Raises:
            UserNotFoundError: If user doesn't exist
            InvalidCredentialsError: If password is incorrect
            UserInactiveError: If user account is inactive
            AccountLockedError: If account is locked
        """
        # Find user
        result = await self.db.execute(
            select(AuthUser).where(AuthUser.email == email.lower())
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFoundError(f"User with email {email} not found")
        
        # Check if account is locked
        if user.locked_until and user.locked_until > datetime.now(timezone.utc):
            raise AccountLockedError(
                f"Account is locked until {user.locked_until}",
                locked_until=user.locked_until.isoformat()
            )
        
        # Check if account is active
        if not user.is_active:
            raise UserInactiveError("User account is inactive")
        
        # Verify password
        if not verify_password(password, user.password_hash):
            # Increment failed attempts
            user.failed_login_attempts += 1
            
            # Lock account if max attempts reached
            if user.failed_login_attempts >= self.MAX_FAILED_ATTEMPTS:
                user.locked_until = datetime.now(timezone.utc) + timedelta(
                    minutes=self.LOCKOUT_DURATION_MINUTES
                )
            
            await self.db.commit()
            raise InvalidCredentialsError("Invalid email or password")
        
        # Reset failed attempts on successful login
        user.failed_login_attempts = 0
        user.locked_until = None
        user.last_login_at = datetime.now(timezone.utc)
        await self.db.commit()
        
        # Invalidate and refresh cache
        await AuthCache.invalidate_user(user.id)
        await AuthCache.set_user(user)
        
        # Generate tokens
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email
        )
        
        plain_refresh_token = create_refresh_token()
        refresh_token_hash = hash_password(plain_refresh_token)
        
        # Store refresh token
        refresh_token = RefreshToken(
            user_id=user.id,
            token_hash=refresh_token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(days=self.REFRESH_TOKEN_EXPIRE_DAYS),
            device_info=device_info
        )
        self.db.add(refresh_token)
        await self.db.commit()
        
        return user, access_token, plain_refresh_token
    
    async def refresh_access_token(self, refresh_token: str) -> str:
        """
        Generate a new access token using a refresh token.
        
        Args:
            refresh_token: Plain text refresh token
            
        Returns:
            New access token
            
        Raises:
            InvalidTokenError: If refresh token is invalid
            RefreshTokenRevokedError: If refresh token has been revoked
            TokenExpiredError: If refresh token has expired
        """
        # Find refresh token in database
        # We need to check all refresh tokens for this user and verify the hash
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        all_tokens = result.scalars().all()
        
        matching_token = None
        for token in all_tokens:
            if verify_password(refresh_token, token.token_hash):
                matching_token = token
                break
        
        if not matching_token:
            raise InvalidTokenError("Invalid refresh token")
        
        if matching_token.is_revoked or matching_token.revoked_at:
            raise RefreshTokenRevokedError("Refresh token has been revoked")
        
        if matching_token.expires_at < datetime.now(timezone.utc):
            raise TokenExpiredError("Refresh token has expired")
        
        # Get user
        user_result = await self.db.execute(
            select(AuthUser).where(AuthUser.id == matching_token.user_id)
        )
        user = user_result.scalar_one()
        
        if not user.is_active:
            raise UserInactiveError("User account is inactive")
        
        # Generate new access token
        access_token = create_access_token(
            user_id=str(user.id),
            email=user.email
        )
        
        return access_token
    
    async def logout(self, refresh_token: str) -> None:
        """
        Revoke a refresh token (logout).
        
        Args:
            refresh_token: Plain text refresh token to revoke
        """
        # Find and revoke refresh token
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.is_revoked == False,
                RefreshToken.expires_at > datetime.now(timezone.utc)
            )
        )
        all_tokens = result.scalars().all()
        
        for token in all_tokens:
            if verify_password(refresh_token, token.token_hash):
                token.is_revoked = True
                token.revoked_at = datetime.now(timezone.utc)
                await self.db.commit()
                return
        
        # Token not found - silently succeed (idempotent)
    
    async def logout_all_devices(self, user_id: UUID) -> None:
        """
        Revoke all refresh tokens for a user (logout from all devices).
        
        Args:
            user_id: User UUID
        """
        result = await self.db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        )
        tokens = result.scalars().all()
        
        now = datetime.now(timezone.utc)
        for token in tokens:
            token.is_revoked = True
            token.revoked_at = now
            # Invalidate refresh token cache
            await AuthCache.invalidate_refresh_token(token.token_hash)
        
        await self.db.commit()
        
        # Invalidate user cache to force refresh
        await AuthCache.invalidate_user(user_id)
    
    async def request_password_reset(self, email: str) -> str:
        """
        Request a password reset token.
        
        Args:
            email: User email
            
        Returns:
            Password reset token (plain text)
            
        Raises:
            UserNotFoundError: If user doesn't exist
        """
        # Find user
        result = await self.db.execute(
            select(AuthUser).where(AuthUser.email == email.lower())
        )
        user = result.scalar_one_or_none()
        
        if not user:
            # Don't reveal if user exists (security best practice)
            # Return a token anyway, but it won't work
            raise UserNotFoundError("If this email exists, a password reset link has been sent")
        
        # Generate reset token
        reset_token = create_refresh_token()
        reset_token_hash = hash_password(reset_token)
        
        # Store reset token
        reset_token_record = PasswordResetToken(
            user_id=user.id,
            token_hash=reset_token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                hours=self.PASSWORD_RESET_EXPIRE_HOURS
            )
        )
        self.db.add(reset_token_record)
        await self.db.commit()
        
        return reset_token
    
    async def reset_password(
        self,
        reset_token: str,
        new_password: str
    ) -> AuthUser:
        """
        Reset password using a reset token.
        
        Args:
            reset_token: Password reset token
            new_password: New plain text password
            
        Returns:
            Updated user
            
        Raises:
            InvalidTokenError: If reset token is invalid or expired
            ValueError: If password doesn't meet requirements
        """
        # Validate password strength
        is_valid, error_msg = check_password_strength(new_password)
        if not is_valid:
            raise ValueError(error_msg or "Password does not meet requirements")
        
        # Find valid reset token
        result = await self.db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(timezone.utc)
            )
        )
        all_tokens = result.scalars().all()
        
        matching_token = None
        for token in all_tokens:
            if verify_password(reset_token, token.token_hash):
                matching_token = token
                break
        
        if not matching_token:
            raise InvalidTokenError("Invalid or expired password reset token")
        
        # Get user
        user_result = await self.db.execute(
            select(AuthUser).where(AuthUser.id == matching_token.user_id)
        )
        user = user_result.scalar_one()
        
        # Update password
        user.password_hash = hash_password(new_password)
        user.failed_login_attempts = 0
        user.locked_until = None
        
        # Mark token as used
        matching_token.used_at = datetime.now(timezone.utc)
        
        # Revoke all refresh tokens (force re-login)
        await self.logout_all_devices(user.id)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        return user
    
    async def request_email_verification(self, user_id: UUID) -> str:
        """
        Request an email verification token.
        
        Args:
            user_id: User UUID
            
        Returns:
            Email verification token (plain text)
        """
        # Get user
        result = await self.db.execute(
            select(AuthUser).where(AuthUser.id == user_id)
        )
        user = result.scalar_one_or_none()
        
        if not user:
            raise UserNotFoundError("User not found")
        
        if user.is_verified:
            raise ValueError("Email is already verified")
        
        # Generate verification token
        verification_token = create_refresh_token()
        verification_token_hash = hash_password(verification_token)
        
        # Store verification token
        verify_token_record = EmailVerificationToken(
            user_id=user.id,
            token_hash=verification_token_hash,
            expires_at=datetime.now(timezone.utc) + timedelta(
                hours=self.EMAIL_VERIFICATION_EXPIRE_HOURS
            )
        )
        self.db.add(verify_token_record)
        await self.db.commit()
        
        return verification_token
    
    async def verify_email(self, verification_token: str) -> AuthUser:
        """
        Verify user email using verification token.
        
        Args:
            verification_token: Email verification token
            
        Returns:
            Updated user
            
        Raises:
            InvalidTokenError: If verification token is invalid or expired
        """
        # Find valid verification token
        result = await self.db.execute(
            select(EmailVerificationToken).where(
                EmailVerificationToken.verified_at.is_(None),
                EmailVerificationToken.expires_at > datetime.now(timezone.utc)
            )
        )
        all_tokens = result.scalars().all()
        
        matching_token = None
        for token in all_tokens:
            if verify_password(verification_token, token.token_hash):
                matching_token = token
                break
        
        if not matching_token:
            raise InvalidTokenError("Invalid or expired email verification token")
        
        # Get user
        user_result = await self.db.execute(
            select(AuthUser).where(AuthUser.id == matching_token.user_id)
        )
        user = user_result.scalar_one()
        
        # Mark email as verified
        user.is_verified = True
        user.email_verified_at = datetime.now(timezone.utc)
        
        # Mark token as used
        matching_token.verified_at = datetime.now(timezone.utc)
        
        await self.db.commit()
        await self.db.refresh(user)
        
        # Invalidate and refresh cache
        await AuthCache.invalidate_user(user.id)
        await AuthCache.set_user(user)
        
        return user
    
    async def get_user_by_id(self, user_id: UUID) -> Optional[AuthUser]:
        """
        Get user by ID.
        
        Args:
            user_id: User UUID
            
        Returns:
            User or None if not found
        """
        result = await self.db.execute(
            select(AuthUser).where(AuthUser.id == user_id)
        )
        return result.scalar_one_or_none()
    
    async def get_user_by_email(self, email: str) -> Optional[AuthUser]:
        """
        Get user by email.
        
        Args:
            email: User email
            
        Returns:
            User or None if not found
        """
        result = await self.db.execute(
            select(AuthUser).where(AuthUser.email == email.lower())
        )
        return result.scalar_one_or_none()

