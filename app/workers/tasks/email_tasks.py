"""
Email tasks for Celery.
"""
import logging
from typing import Optional
from app.workers.celery_app import celery_app
from app.services.email_service import (
    send_email_sync,
    render_template,
    EmailService,
)
from app.config import settings

logger = logging.getLogger(__name__)


@celery_app.task(name="send_verification_email_task", bind=True, max_retries=3)
def send_verification_email_task(
    self,
    to_email: str,
    verification_token: str,
    user_name: Optional[str] = None
) -> None:
    """
    Send email verification email (Celery task).
    
    Args:
        to_email: Recipient email address
        verification_token: Email verification token
        user_name: User's name (optional)
    """
    logger.info(f"Starting verification email task for {to_email}")
    try:
        EmailService.send_verification_email_sync(
            to_email=to_email,
            verification_token=verification_token,
            user_name=user_name
        )
        logger.info(f"Successfully sent verification email to {to_email}")
    except Exception as exc:
        logger.error(f"Failed to send verification email to {to_email}: {exc}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="send_password_reset_email_task", bind=True, max_retries=3)
def send_password_reset_email_task(
    self,
    to_email: str,
    reset_token: str,
    user_name: Optional[str] = None
) -> None:
    """
    Send password reset email (Celery task).
    
    Args:
        to_email: Recipient email address
        reset_token: Password reset token
        user_name: User's name (optional)
    """
    try:
        EmailService.send_password_reset_email_sync(
            to_email=to_email,
            reset_token=reset_token,
            user_name=user_name
        )
    except Exception as exc:
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))


@celery_app.task(name="send_welcome_email_task", bind=True, max_retries=3)
def send_welcome_email_task(
    self,
    to_email: str,
    user_name: Optional[str] = None
) -> None:
    """
    Send welcome email (Celery task).
    
    Args:
        to_email: Recipient email address
        user_name: User's name (optional)
    """
    logger.info(f"Starting welcome email task for {to_email}")
    try:
        EmailService.send_welcome_email_sync(
            to_email=to_email,
            user_name=user_name
        )
        logger.info(f"Successfully sent welcome email to {to_email}")
    except Exception as exc:
        logger.error(f"Failed to send welcome email to {to_email}: {exc}", exc_info=True)
        # Retry with exponential backoff
        raise self.retry(exc=exc, countdown=60 * (2 ** self.request.retries))

