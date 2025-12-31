"""
Token refresh endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import RefreshTokenRequest, TokenResponse
from app.auth.service import AuthService
from app.auth.exceptions import (
    InvalidTokenError,
    RefreshTokenRevokedError,
    TokenExpiredError,
    UserInactiveError,
)
from app.config import settings

router = APIRouter()


@router.post(
    "/refresh",
    response_model=TokenResponse,
    status_code=status.HTTP_200_OK,
    summary="Refresh access token",
    description="Generate a new access token using refresh token"
)
async def refresh_token(
    request: RefreshTokenRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Refresh access token.
    
    Args:
        request: Refresh token request
        db: Database session
        
    Returns:
        New access token
        
    Raises:
        HTTPException: If refresh fails
    """
    auth_service = AuthService(db)
    
    try:
        access_token = await auth_service.refresh_access_token(
            refresh_token=request.refresh_token
        )
        
        return TokenResponse(
            access_token=access_token,
            refresh_token=request.refresh_token,  # Return same refresh token
            token_type="bearer",
            expires_in=settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES * 60
        )
        
    except (InvalidTokenError, RefreshTokenRevokedError, TokenExpiredError) as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(e)
        )
    except UserInactiveError:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User account is inactive"
        )

