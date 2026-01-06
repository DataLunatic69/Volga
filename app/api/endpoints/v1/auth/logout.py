"""
Logout endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import LogoutRequest, MessageResponse
from app.auth.service import AuthService
from app.auth.dependencies import get_current_active_user, get_current_user
from app.auth.jwt import decode_token
from app.database.models import AuthUser

router = APIRouter()


@router.post(
    "/logout",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="User logout",
    description="Revoke refresh token and logout user"
)
async def logout(
    request: LogoutRequest,
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
    authorization: str = Header(None),
):
    """
    Logout user by revoking refresh token and blacklisting access token.
    
    Args:
        request: Logout request with refresh token
        current_user: Current authenticated user
        db: Database session
        authorization: Authorization header (for extracting access token JTI)
        
    Returns:
        Success message
    """
    auth_service = AuthService(db)
    
    # Extract access token JTI for blacklisting
    access_token_jti = None
    if authorization and authorization.startswith("Bearer "):
        token = authorization.split(" ")[1]
        try:
            payload = decode_token(token, verify=False)
            access_token_jti = payload.get("jti")
        except Exception:
            pass  # Ignore errors, continue with logout
    
    try:
        await auth_service.logout(
            refresh_token=request.refresh_token,
            access_token_jti=access_token_jti
        )
        
        return MessageResponse(
            message="Logged out successfully"
        )
    except Exception:
        # Silently succeed even if token not found (idempotent)
        return MessageResponse(
            message="Logged out successfully"
        )


@router.post(
    "/logout-all",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Logout from all devices",
    description="Revoke all refresh tokens for the current user"
)
async def logout_all(
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Logout from all devices.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    auth_service = AuthService(db)
    
    await auth_service.logout_all_devices(user_id=current_user.id)
    
    return MessageResponse(
        message="Logged out from all devices successfully"
    )

