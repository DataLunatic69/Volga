"""
Authentication module for NexCell AI Receptionist.
Handles user authentication, JWT tokens, password management, and authorization.
"""
from .password import verify_password, hash_password
from .jwt import create_access_token, create_refresh_token, verify_token, decode_token
from .cache import AuthCache, CacheKeys, CacheTTL
from .service import AuthService
from .schemas import (
    RegisterRequest,
    LoginRequest,
    RefreshTokenRequest,
    LogoutRequest,
    ForgotPasswordRequest,
    ResetPasswordRequest,
    VerifyEmailRequest,
    ResendVerificationRequest,
    TokenResponse,
    UserResponse,
    AuthResponse,
    MessageResponse,
    ErrorResponse,
)
from .dependencies import (
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_current_agency,
    get_optional_current_user,
)
from .permissions import (
    require_permission,
    require_role,
    require_any_permission,
    require_all_permissions,
    require_ownership,
    get_current_agency_id,
    get_user_with_permissions,
    check_permission_programmatic,
    require_permission_programmatic,
)
from .permission_cache import PermissionCache, permission_cache
from .exceptions import (
    AuthenticationError,
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

__all__ = [
    # Password utilities
    "verify_password",
    "hash_password",
    # JWT utilities
    "create_access_token",
    "create_refresh_token",
    "verify_token",
    "decode_token",
    # Cache
    "AuthCache",
    "CacheKeys",
    "CacheTTL",
    # Service
    "AuthService",
    # Schemas
    "RegisterRequest",
    "LoginRequest",
    "RefreshTokenRequest",
    "LogoutRequest",
    "ForgotPasswordRequest",
    "ResetPasswordRequest",
    "VerifyEmailRequest",
    "ResendVerificationRequest",
    "TokenResponse",
    "UserResponse",
    "AuthResponse",
    "MessageResponse",
    "ErrorResponse",
    # Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_current_agency",
    "get_optional_current_user",
    # Permission dependencies
    "require_permission",
    "require_role",
    "require_any_permission",
    "require_all_permissions",
    "require_ownership",
    "get_current_agency_id",
    "get_user_with_permissions",
    "check_permission_programmatic",
    "require_permission_programmatic",
    # Permission cache
    "PermissionCache",
    "permission_cache",
    # Exceptions
    "AuthenticationError",
    "InvalidCredentialsError",
    "UserNotFoundError",
    "UserAlreadyExistsError",
    "UserInactiveError",
    "UserNotVerifiedError",
    "AccountLockedError",
    "TokenExpiredError",
    "InvalidTokenError",
    "RefreshTokenRevokedError",
]

