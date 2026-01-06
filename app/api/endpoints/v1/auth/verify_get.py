"""
GET endpoint for email verification (clickable from email).
"""
from fastapi import APIRouter, Depends, Path
from fastapi.responses import HTMLResponse
from sqlalchemy.ext.asyncio import AsyncSession
from jinja2 import Environment, FileSystemLoader
from pathlib import Path as FilePath

from app.database.session import get_db
from app.auth.service import AuthService
from app.auth.exceptions import InvalidTokenError
from app.config import settings

router = APIRouter()

# Setup Jinja2 for response templates
TEMPLATE_DIR = FilePath(__file__).resolve().parent.parent.parent.parent.parent / "app" / "templates" / "responses"
jinja_env = Environment(loader=FileSystemLoader(str(TEMPLATE_DIR)))


@router.get(
    "/verify-email/{token}",
    response_class=HTMLResponse,
    summary="Verify email via GET (clickable link)",
    description="Verify user email by clicking link from email. Returns HTML page.",
    tags=["Authentication"]
)
async def verify_email_get(
    token: str = Path(..., description="Email verification token"),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify email address via GET request (clickable from email).
    
    This endpoint is designed to be called directly from email links.
    It validates the token and returns an HTML page showing success or failure.
    
    Args:
        token: Email verification token from URL path
        db: Database session
        
    Returns:
        HTML page showing verification result
    """
    auth_service = AuthService(db)
    
    try:
        # Verify email with proper transaction handling
        user = await auth_service.verify_email(verification_token=token)
        
        # Render success page
        template = jinja_env.get_template("email_verified.html")
        html_content = template.render(
            app_name=settings.APP_NAME,
            email=user.email
        )
        
        return HTMLResponse(
            content=html_content,
            status_code=200
        )
        
    except InvalidTokenError as e:
        # Render error page
        template = jinja_env.get_template("verification_error.html")
        html_content = template.render(
            error_message=str(e)
        )
        
        return HTMLResponse(
            content=html_content,
            status_code=400
        )
    except Exception as e:
        # Render generic error page
        template = jinja_env.get_template("verification_error.html")
        html_content = template.render(
            error_message="An unexpected error occurred. Please try again or contact support."
        )
        
        return HTMLResponse(
            content=html_content,
            status_code=500
        )

