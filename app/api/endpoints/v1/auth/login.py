"""
Login endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Request
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import LoginRequest, AuthResponse
from app.auth.service import AuthService
from app.auth.exceptions import (
    InvalidCredentialsError,
    UserNotFoundError,
    UserInactiveError,
    AccountLockedError,
)
from app.config import settings

router = APIRouter()


@router.post(
    "/login",
    response_model=AuthResponse,
    status_code=status.HTTP_200_OK,
    summary="User login",
    description="Authenticate user and return access/refresh tokens"
)
async def login(
    request: LoginRequest,
    db: AsyncSession = Depends(get_db),
    http_request: Request = None,
):
    """
    Login endpoint.
    
    Args:
        request: Login credentials
        db: Database session
        http_request: FastAPI request object (optional, for device info)
        
    Returns:
        User info and tokens
        
    Raises:
        HTTPException: If login fails
    """
    auth_service = AuthService(db)
    
    # Prepare device info from request headers
    device_info = None
    if http_request:
        device_info = {}
        user_agent = http_request.headers.get("user-agent")
        x_forwarded_for = http_request.headers.get("x-forwarded-for")
        if user_agent:
            device_info["user_agent"] = user_agent
        if x_forwarded_for:
            device_info["ip_address"] = x_forwarded_for.split(",")[0].strip()
        if not device_info:
            device_info = None
    
    try:
        user, access_token, refresh_token = await auth_service.login(
            email=request.email,
            password=request.password,
            device_info=device_info if device_info else None
        )
        
        # Create response
        from app.auth.schemas import UserResponse, TokenResponse
        
        return AuthResponse(
            user=UserResponse.model_validate(user),
            tokens=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                token_type="bearer",
                expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
            )
        )
        
    except InvalidCredentialsError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )
    except UserNotFoundError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"  # Don't reveal if user exists
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )
    except AccountLockedError as e:
        raise HTTPException(
            status_code=status.HTTP_423_LOCKED,
            detail=str(e)
        )

