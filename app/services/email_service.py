"""
Email service using FastMail for sending emails.
"""
from typing import List, Optional, Dict, Any
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, select_autoescape

from fastapi_mail import FastMail, ConnectionConfig, MessageSchema, MessageType
from asgiref.sync import async_to_sync

from app.config import settings

# Template directory
BASE_DIR = Path(__file__).resolve().parent.parent
TEMPLATE_DIR = BASE_DIR / "templates" / "email"

# Jinja2 environment for templates
jinja_env = Environment(
    loader=FileSystemLoader(str(TEMPLATE_DIR)),
    autoescape=select_autoescape(['html', 'xml'])
)


def get_mail_config() -> ConnectionConfig:
    """
    Get FastMail connection configuration.
    
    Returns:
        ConnectionConfig for FastMail
        
    Raises:
        ValueError: If required email settings are missing
    """
    if not settings.MAIL_SERVER:
        raise ValueError("MAIL_SERVER is required for email functionality")
    if not settings.MAIL_USERNAME:
        raise ValueError("MAIL_USERNAME is required for email functionality")
    if not settings.MAIL_PASSWORD:
        raise ValueError("MAIL_PASSWORD is required for email functionality")
    if not settings.MAIL_FROM:
        raise ValueError("MAIL_FROM is required for email functionality")
    
    return ConnectionConfig(
        MAIL_USERNAME=settings.MAIL_USERNAME,
        MAIL_PASSWORD=settings.MAIL_PASSWORD,
        MAIL_FROM=settings.MAIL_FROM,
        MAIL_FROM_NAME=settings.MAIL_FROM_NAME or settings.APP_NAME,
        MAIL_PORT=settings.MAIL_PORT,
        MAIL_SERVER=settings.MAIL_SERVER,
        MAIL_STARTTLS=settings.MAIL_STARTTLS,
        MAIL_SSL_TLS=settings.MAIL_SSL_TLS,
        USE_CREDENTIALS=True,
        VALIDATE_CERTS=True,
        TEMPLATE_FOLDER=str(TEMPLATE_DIR),
    )


# Initialize FastMail instance (lazy initialization)
mail: Optional[FastMail] = None


def get_mail() -> Optional[FastMail]:
    """
    Get FastMail instance, initializing if needed.
    
    Returns:
        FastMail instance or None if not configured
    """
    global mail
    if mail is None:
        try:
            mail_config = get_mail_config()
            mail = FastMail(mail_config)
        except ValueError:
            # Email not configured, return None
            return None
    return mail


def render_template(template_name: str, context: Dict[str, Any]) -> str:
    """
    Render email template with context.
    
    Args:
        template_name: Name of template file (e.g., "verification.html")
        context: Template context variables
        
    Returns:
        Rendered HTML string
    """
    template = jinja_env.get_template(template_name)
    return template.render(**context)


def create_message(
    recipients: List[str],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html
) -> MessageSchema:
    """
    Create email message.
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body (HTML or plain text)
        subtype: Message type (html or plain)
        
    Returns:
        MessageSchema instance
    """
    return MessageSchema(
        recipients=recipients,
        subject=subject,
        body=body,
        subtype=subtype
    )


async def send_email_async(
    recipients: List[str],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html
) -> None:
    """
    Send email asynchronously.
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body
        subtype: Message type
        
    Raises:
        ValueError: If email is not configured
    """
    mail_instance = get_mail()
    if not mail_instance:
        raise ValueError("Email service is not configured. Set MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, and MAIL_FROM")
    
    message = create_message(recipients, subject, body, subtype)
    await mail_instance.send_message(message)


def send_email_sync(
    recipients: List[str],
    subject: str,
    body: str,
    subtype: MessageType = MessageType.html
) -> None:
    """
    Send email synchronously (for use in Celery tasks).
    
    Args:
        recipients: List of recipient email addresses
        subject: Email subject
        body: Email body
        subtype: Message type
        
    Raises:
        ValueError: If email is not configured
    """
    mail_instance = get_mail()
    if not mail_instance:
        raise ValueError("Email service is not configured. Set MAIL_SERVER, MAIL_USERNAME, MAIL_PASSWORD, and MAIL_FROM")
    
    message = create_message(recipients, subject, body, subtype)
    async_to_sync(mail_instance.send_message)(message)


class EmailService:
    """Email service for sending various types of emails."""
    
    # Note: Frontend URL removed - backend only for now
    # When frontend is configured, add FRONTEND_URL back to settings
    
    @staticmethod
    async def send_verification_email(
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None
    ) -> None:
        """
        Send email verification email.
        
        Args:
            to_email: Recipient email address
            verification_token: Email verification token
            user_name: User's name (optional)
        """
        # Create full URL with backend domain for clickable email link
        verification_link = f"{settings.BACKEND_DOMAIN}/api/v1/verify-email/{verification_token}"
        
        context = {
            "user_name": user_name or "User",
            "verification_link": verification_link,
            "app_name": settings.APP_NAME,
        }
        
        body = render_template("verification.html", context)
        subject = f"Verify your {settings.APP_NAME} account"
        
        await send_email_async([to_email], subject, body)
    
    @staticmethod
    async def send_password_reset_email(
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> None:
        """
        Send password reset email.
        
        Args:
            to_email: Recipient email address
            reset_token: Password reset token
            user_name: User's name (optional)
        """
        # Create full URL with backend domain for clickable email link
        reset_link = f"{settings.BACKEND_DOMAIN}/api/v1/reset-password/{reset_token}"
        
        context = {
            "user_name": user_name or "User",
            "reset_link": reset_link,
            "app_name": settings.APP_NAME,
            "expiry_hours": 1,  # Password reset tokens expire in 1 hour
        }
        
        body = render_template("password_reset.html", context)
        subject = f"Reset your {settings.APP_NAME} password"
        
        await send_email_async([to_email], subject, body)
    
    @staticmethod
    async def send_welcome_email(
        to_email: str,
        user_name: Optional[str] = None
    ) -> None:
        """
        Send welcome email to new users.
        
        Args:
            to_email: Recipient email address
            user_name: User's name (optional)
        """
        context = {
            "user_name": user_name or "User",
            "app_name": settings.APP_NAME,
            "login_link": "login",  # Backend only - frontend will handle routing
        }
        
        body = render_template("welcome.html", context)
        subject = f"Welcome to {settings.APP_NAME}!"
        
        await send_email_async([to_email], subject, body)
    
    # Synchronous versions for Celery tasks
    @staticmethod
    def send_verification_email_sync(
        to_email: str,
        verification_token: str,
        user_name: Optional[str] = None
    ) -> None:
        """Synchronous version for Celery tasks."""
        # Create full URL with backend domain for clickable email link
        verification_link = f"{settings.BACKEND_DOMAIN}/api/v1/verify-email/{verification_token}"
        
        context = {
            "user_name": user_name or "User",
            "verification_link": verification_link,
            "app_name": settings.APP_NAME,
        }
        
        body = render_template("verification.html", context)
        subject = f"Verify your {settings.APP_NAME} account"
        
        send_email_sync([to_email], subject, body)
    
    @staticmethod
    def send_password_reset_email_sync(
        to_email: str,
        reset_token: str,
        user_name: Optional[str] = None
    ) -> None:
        """Synchronous version for Celery tasks."""
        # Create full URL with backend domain for clickable email link
        reset_link = f"{settings.BACKEND_DOMAIN}/api/v1/reset-password/{reset_token}"
        
        context = {
            "user_name": user_name or "User",
            "reset_link": reset_link,
            "app_name": settings.APP_NAME,
            "expiry_hours": 1,
        }
        
        body = render_template("password_reset.html", context)
        subject = f"Reset your {settings.APP_NAME} password"
        
        send_email_sync([to_email], subject, body)
    
    @staticmethod
    def send_welcome_email_sync(
        to_email: str,
        user_name: Optional[str] = None
    ) -> None:
        """Synchronous version for Celery tasks."""
        context = {
            "user_name": user_name or "User",
            "app_name": settings.APP_NAME,
            "login_link": "login",  # Backend only - frontend will handle routing
        }
        
        body = render_template("welcome.html", context)
        subject = f"Welcome to {settings.APP_NAME}!"
        
        send_email_sync([to_email], subject, body)

