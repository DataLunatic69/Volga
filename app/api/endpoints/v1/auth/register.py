"""
Registration endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import RegisterRequest, AuthResponse
from app.auth.service import AuthService
from app.auth.exceptions import UserAlreadyExistsError
from app.config import settings

router = APIRouter()


@router.post(
    "/register",
    response_model=AuthResponse,
    status_code=status.HTTP_201_CREATED,
    summary="User registration",
    description="Register a new user account"
)
async def register(
    request: RegisterRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Register a new user.
    
    Args:
        request: Registration data
        db: Database session
        
    Returns:
        User info and tokens
        
    Raises:
        HTTPException: If registration fails
    """
    auth_service = AuthService(db)
    
    try:
        user, access_token, refresh_token = await auth_service.register(
            email=request.email,
            password=request.password,
            full_name=request.full_name
        )
        
        # Send verification email via background task
        verification_token = await auth_service.request_email_verification(user.id)
        from app.workers.tasks.email_tasks import send_verification_email_task, send_welcome_email_task
        
        send_verification_email_task.delay(
            to_email=user.email,
            verification_token=verification_token,
            user_name=request.full_name
        )
        
        # Send welcome email
        send_welcome_email_task.delay(
            to_email=user.email,
            user_name=request.full_name
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
        
    except UserAlreadyExistsError:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User with this email already exists"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

