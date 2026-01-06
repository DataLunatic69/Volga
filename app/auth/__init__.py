"""
Authentication module for NexCell AI Receptionist.
Handles user authentication, JWT tokens, password management, and authorization.
"""
from .password import verify_password, hash_password
from .jwt import create_access_token, create_refresh_token, verify_token, decode_token
from .token_utils import hash_token, verify_token_hash, create_token_with_prefix, extract_token_prefix
from .cache import AuthCache, CacheKeys, CacheTTL, permission_cache
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
# FastAPI Dependencies (from dependencies.py)
from .dependencies import (
    # Core auth
    get_current_user,
    get_current_active_user,
    get_current_verified_user,
    get_optional_current_user,
    get_optional_verified_user,
    # Role-based
    get_current_admin_user,
    get_current_superuser,
    # Agency context
    extract_agency_id,
    get_required_agency_id,
    verify_agency_membership,
    get_agency_or_404,
    get_current_agency,
    get_user_with_agency,
    # Permission dependencies
    require_permission,
    require_role,
    require_any_permission,
    require_all_permissions,
    require_ownership,
    get_user_with_permissions,
    get_permission_service,
)
# Business Logic (from permissions.py - programmatic use)
from .permissions import (
    check_permission,
    check_any_permission,
    check_all_permissions,
    check_role,
    get_user_permissions_cached,
    get_user_roles,
    invalidate_user_permissions,
    invalidate_role_permissions,
)
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
    PermissionDeniedError,
    ResourceNotFoundError,
    InvalidInputError,
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
    # Token utilities (fast hashing)
    "hash_token",
    "verify_token_hash",
    "create_token_with_prefix",
    "extract_token_prefix",
    # Cache
    "AuthCache",
    "CacheKeys",
    "CacheTTL",
    "permission_cache",
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
    # Core Auth Dependencies
    "get_current_user",
    "get_current_active_user",
    "get_current_verified_user",
    "get_optional_current_user",
    "get_optional_verified_user",
    # Role-based Dependencies
    "get_current_admin_user",
    "get_current_superuser",
    # Agency Context Dependencies
    "extract_agency_id",
    "get_required_agency_id",
    "verify_agency_membership",
    "get_agency_or_404",
    "get_current_agency",
    "get_user_with_agency",
    # Permission Dependencies (FastAPI)
    "require_permission",
    "require_role",
    "require_any_permission",
    "require_all_permissions",
    "require_ownership",
    "get_user_with_permissions",
    "get_permission_service",
    # Permission Business Logic (programmatic)
    "check_permission",
    "check_any_permission",
    "check_all_permissions",
    "check_role",
    "get_user_permissions_cached",
    "get_user_roles",
    "invalidate_user_permissions",
    "invalidate_role_permissions",
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
    "PermissionDeniedError",
    "ResourceNotFoundError",
    "InvalidInputError",
]
