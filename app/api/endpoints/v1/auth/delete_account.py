"""
Delete account endpoint.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.database.session import get_db
from app.auth.schemas import MessageResponse
from app.auth.dependencies import get_current_active_user
from app.database.models import AuthUser, RefreshToken, EmailVerificationToken, PasswordResetToken
from app.auth.cache import AuthCache

router = APIRouter()


@router.delete(
    "/me",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Delete user account",
    description="Permanently delete the current user's account and all associated data"
)
async def delete_account(
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete current user account.
    
    This endpoint permanently deletes:
    - User account
    - All refresh tokens
    - All verification tokens
    - All password reset tokens
    - User cache
    
    **Warning**: This action is irreversible!
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
        
    Raises:
        HTTPException: If deletion fails
    """
    user_id = current_user.id
    
    try:
        # 1. Delete all refresh tokens
        refresh_tokens_result = await db.execute(
            select(RefreshToken).where(RefreshToken.user_id == user_id)
        )
        refresh_tokens = refresh_tokens_result.scalars().all()
        
        for token in refresh_tokens:
            # Invalidate refresh token cache
            await AuthCache.invalidate_refresh_token(token.token_hash)
            await db.delete(token)
        
        # 2. Delete all email verification tokens
        verification_tokens_result = await db.execute(
            select(EmailVerificationToken).where(EmailVerificationToken.user_id == user_id)
        )
        verification_tokens = verification_tokens_result.scalars().all()
        
        for token in verification_tokens:
            await db.delete(token)
        
        # 3. Delete all password reset tokens
        reset_tokens_result = await db.execute(
            select(PasswordResetToken).where(PasswordResetToken.user_id == user_id)
        )
        reset_tokens = reset_tokens_result.scalars().all()
        
        for token in reset_tokens:
            await db.delete(token)
        
        # 4. Invalidate user cache
        await AuthCache.invalidate_user(user_id)
        
        # 5. Delete user account
        await db.delete(current_user)
        
        # 6. Commit all deletions
        await db.commit()
        
        return MessageResponse(
            message="Account deleted successfully. All your data has been permanently removed."
        )
        
    except Exception as e:
        await db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deleting account {user_id}: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete account. Please try again or contact support."
        )


@router.post(
    "/me/deactivate",
    response_model=MessageResponse,
    status_code=status.HTTP_200_OK,
    summary="Deactivate user account",
    description="Deactivate the current user's account (can be reactivated later)"
)
async def deactivate_account(
    current_user: AuthUser = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Deactivate current user account (soft delete).
    
    This endpoint deactivates the account instead of permanently deleting it.
    The user can reactivate by logging in again.
    
    Deactivation:
    - Sets is_active to False
    - Revokes all refresh tokens
    - Invalidates user cache
    - Preserves all user data
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Success message
    """
    user_id = current_user.id
    
    try:
        # 1. Deactivate user
        current_user.is_active = False
        
        # 2. Revoke all refresh tokens
        refresh_tokens_result = await db.execute(
            select(RefreshToken).where(
                RefreshToken.user_id == user_id,
                RefreshToken.is_revoked == False
            )
        )
        refresh_tokens = refresh_tokens_result.scalars().all()
        
        from datetime import datetime, timezone
        now = datetime.now(timezone.utc)
        
        for token in refresh_tokens:
            token.is_revoked = True
            token.revoked_at = now
            # Invalidate refresh token cache
            await AuthCache.invalidate_refresh_token(token.token_hash)
        
        # 3. Invalidate user cache
        await AuthCache.invalidate_user(user_id)
        
        # 4. Commit changes
        await db.commit()
        
        return MessageResponse(
            message="Account deactivated successfully. You can reactivate by logging in again."
        )
        
    except Exception as e:
        await db.rollback()
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error deactivating account {user_id}: {str(e)}")
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to deactivate account. Please try again."
        )

