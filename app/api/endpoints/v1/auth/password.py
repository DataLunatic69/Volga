"""
Password reset endpoints.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database.session import get_db
from app.auth.schemas import (
    ForgotPasswordRequest,
    ResetPasswordRequest,
    MessageResponse
)
from app.auth.service import AuthService
from app.auth.exceptions import UserNotFoundError, InvalidTokenError

router = APIRouter()


@router.post(
    "/forgot-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Request password reset",
    description="Send password reset email"
)
async def forgot_password(
    request: ForgotPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Request password reset.
    
    Args:
        request: Email address
        db: Database session
        
    Returns:
        Success message (always returns success for security)
    """
    auth_service = AuthService(db)
    
    try:
        reset_token = await auth_service.request_password_reset(
            email=request.email
        )
        
        # Send password reset email via background task
        from app.workers.tasks.email_tasks import send_password_reset_email_task
        
        try:
            send_password_reset_email_task.delay(
                to_email=request.email,
                reset_token=reset_token,
                user_name=None  # We don't have user name in forgot password request
            )
        except Exception as e:
            import logging
            logger = logging.getLogger(__name__)
            logger.error(f"Failed to queue password reset email for {request.email}: {e}", exc_info=True)
            # Don't re-raise, allow request to complete
        
        # Always return success message (don't reveal if user exists)
        return MessageResponse(
            message="If this email exists, a password reset link has been sent"
        )
        
    except UserNotFoundError:
        # Still return success for security
        return MessageResponse(
            message="If this email exists, a password reset link has been sent"
        )


@router.post(
    "/reset-password",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Reset password",
    description="Reset password using reset token"
)
async def reset_password(
    request: ResetPasswordRequest,
    db: AsyncSession = Depends(get_db),
):
    """
    Reset password using reset token.
    
    Args:
        request: Reset token and new password
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If reset fails
    """
    auth_service = AuthService(db)
    
    try:
        await auth_service.reset_password(
            reset_token=request.token,
            new_password=request.new_password
        )
        
        return MessageResponse(
            message="Password reset successfully"
        )
        
    except InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired reset token"
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

