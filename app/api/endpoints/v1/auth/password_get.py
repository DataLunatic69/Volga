"""
GET endpoint for password reset (clickable from email).
"""
from fastapi import APIRouter, Depends, Path
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from jinja2 import Environment, FileSystemLoader
from pathlib import Path as FilePath
from datetime import datetime, timezone

from app.database.session import get_db
from app.database.models import PasswordResetToken
from app.auth.password import verify_password
from app.config import settings

router = APIRouter()

# Setup Jinja2 for response templates
TEMPLATE_DIR = FilePath(__file__).resolve().parent.parent.parent.parent.parent / "app" / "templates" / "responses"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


@router.get(
    "/reset-password/{token}",
    response_class=HTMLResponse,
    summary="Show password reset form (clickable link)",
    description="Display password reset form by clicking link from email. Returns HTML page with form.",
    tags=["Authentication"]
)
async def reset_password_get(
    token: str = Path(..., description="Password reset token"),
    db: AsyncSession = Depends(get_db),
):
    """
    Show password reset form via GET request (clickable from email).
    
    This endpoint is designed to be called directly from email links.
    It validates the token and returns an HTML form for the user to enter a new password.
    
    Args:
        token: Password reset token from URL path
        db: Database session
        
    Returns:
        HTML page with password reset form or error message
    """
    try:
        # Validate token by checking if it exists and isn't expired
        # We'll do a basic check here without consuming the token
        result = await db.execute(
            select(PasswordResetToken).where(
                PasswordResetToken.used_at.is_(None),
                PasswordResetToken.expires_at > datetime.now(timezone.utc)
            )
        )
        all_tokens = result.scalars().all()
        
        # Find matching token by comparing hashes
        token_valid = False
        for db_token in all_tokens:
            if verify_password(token, db_token.token_hash):
                token_valid = True
                break
        
        if not token_valid:
            # Token is invalid or expired - show error page
            template = jinja_env.get_template("password_reset_error.html")
            html_content = template.render(
                error_message="Invalid or expired reset token. Please request a new password reset link."
            )
            
            return HTMLResponse(
                content=html_content,
                status_code=400
            )
        
        # Token is valid - show reset form
        template = jinja_env.get_template("password_reset_form.html")
        html_content = template.render(
            token=token,
            backend_domain=settings.BACKEND_DOMAIN
        )
        
        return HTMLResponse(
            content=html_content,
            status_code=200
        )
        
    except Exception as e:
        # Generic error page
        template = jinja_env.get_template("password_reset_error.html")
        html_content = template.render(
            error_message="An unexpected error occurred. Please try again or contact support."
        )
        
        return HTMLResponse(
            content=html_content,
            status_code=500
        )

