"""
Authentication API endpoints.
"""
from fastapi import APIRouter

from .login import router as login_router
from .register import router as register_router
from .refresh import router as refresh_router
from .logout import router as logout_router
from .password import router as password_router
from .verify import router as verify_router
from .me import router as me_router
from .delete_account import router as delete_account_router
from .verify_get import router as verify_get_router
from .password_get import router as password_get_router

# Create main auth router
router = APIRouter(tags=["Authentication"])

# Include all auth sub-routers
router.include_router(login_router)
router.include_router(register_router)
router.include_router(refresh_router)
router.include_router(logout_router)
router.include_router(password_router)
router.include_router(verify_router)
router.include_router(me_router)
router.include_router(delete_account_router)
# GET endpoints for email links
router.include_router(verify_get_router)
router.include_router(password_get_router)

__all__ = ["router"]
