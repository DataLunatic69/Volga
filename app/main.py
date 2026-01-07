"""
Main FastAPI application entry point.
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.endpoints.v1.auth import router as auth_router
from app.api.middlewares import (
    AuthMiddleware,
    RateLimitingMiddleware,
    LoggingMiddleware,
    SecurityLoggingMiddleware,
)
from app.database.redis import init_redis_cache, close_redis_cache
from app.core.logger import setup_logging


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
    setup_logging()
    await init_redis_cache()
    yield
    # Shutdown
    await close_redis_cache()


# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="NexCell AI Receptionist - AI-powered real estate CRM",
    docs_url="/docs" if settings.DEBUG else None,
    redoc_url="/redoc" if settings.DEBUG else None,
    lifespan=lifespan,
)

# ============================================================
# Middleware Stack (order matters - last added = first executed)
# 
# Request flow:  Client -> CORS -> Logging -> RateLimit -> Auth -> Route
# Response flow: Route -> Auth -> RateLimit -> Logging -> CORS -> Client
# ============================================================

# 1. CORS (outermost - must handle preflight first)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# 2. Request Logging (logs all requests with timing)
app.add_middleware(LoggingMiddleware)

# 3. Security Event Logging (logs auth failures, rate limits)
app.add_middleware(SecurityLoggingMiddleware)

# 4. Rate Limiting (protects against DoS/brute force)
app.add_middleware(RateLimitingMiddleware, enabled=True)

# 5. Authentication (validates JWT, attaches user)
app.add_middleware(AuthMiddleware, auto_error=True)

# Include routers
app.include_router(auth_router, prefix="/api/v1")


@app.get("/")
def read_root():
    """Root endpoint."""
    return {
        "message": "Welcome to NexCell AI Receptionist API",
        "version": settings.APP_VERSION,
        "docs": "/docs" if settings.DEBUG else "disabled"
    }


@app.get("/health")
def health_check():
    """Health check endpoint."""
    return {"status": "healthy", "version": settings.APP_VERSION}


if __name__ == "__main__":
    uvicorn.run(
        app,
        host=settings.API_HOST,
        port=settings.API_PORT,
        reload=settings.DEBUG
    )
