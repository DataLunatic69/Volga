"""
Email verification endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import (
    VerifyEmailRequest,
    ResendVerificationRequest,
    MessageResponse
)
from app.auth.service import AuthService
from app.auth.exceptions import InvalidTokenError, UserNotFoundError
from app.auth.dependencies import get_current_active_user
from app.database.models import AuthUser

router = APIRouter()


@router.post(
    "/verify-email",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Verify email",
    description="Verify user email using verification token"
)
async def verify_email(
    request: VerifyEmailRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Verify email address.
    
    Args:
        request: Verification token
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If verification fails
    """
    auth_service = AuthService(db)
    
    try:
        await auth_service.verify_email(
            verification_token=request.token
        )
        
        return MessageResponse(
            message="Email verified successfully"
        )
        
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired verification token"
        )


@router.post(
    "/resend-verification",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend verification email",
    description="Resend email verification link"
)
async def resend_verification(
    request: ResendVerificationRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification.
    
    Args:
        request: Email address
        db: Database session
        
    Returns:
        Success message
    """
    auth_service = AuthService(db)
    
    try:
        # Get user by email
        user = await auth_service.get_user_by_email(email=request.email)
        
        if not user:
            # Don't reveal if user exists
            return MessageResponse(
                message="If this email exists, a verification link has been sent"
            )
        
        if user.is_verified:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email is already verified"
            )
        
        # Generate new verification token
        verification_token = await auth_service.request_email_verification(
            user_id=user.id
        )
        
        # Send verification email via background task
        from app.workers.tasks.email_tasks import send_verification_email_task
        
        send_verification_email_task.delay(
            to_email=user.email,
            verification_token=verification_token,
            user_name=None  # We don't have full_name in AuthUser
        )
        
        return MessageResponse(
            message="If this email exists, a verification link has been sent"
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post(
    "/me/resend-verification",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Resend verification email (authenticated)",
    description="Resend email verification link for current user"
)
async def resend_verification_me(
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resend email verification for current user.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    auth_service = AuthService(db)
    
    if current_user.is_verified:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email is already verified"
        )
    
    # Generate new verification token
    verification_token = await auth_service.request_email_verification(
        user_id=current_user.id
    )
    
    # Send verification email via background task
    from app.workers.tasks.email_tasks import send_verification_email_task
    
    send_verification_email_task.delay(
        to_email=current_user.email,
        verification_token=verification_token,
        user_name=None  # We don't have full_name in AuthUser
    )
    
    return MessageResponse(
        message="Verification link has been sent to your email"
    )

