"""
Main FastAPI application entry point.
"""
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.api.endpoints.v1.auth import router as auth_router
from app.api.middlewares.auth_middleware import AuthMiddleware
from app.database.redis import init_redis_cache, close_redis_cache


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for startup/shutdown events."""
    # Startup
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

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=settings.CORS_ALLOW_CREDENTIALS,
    allow_methods=settings.CORS_ALLOW_METHODS,
    allow_headers=settings.CORS_ALLOW_HEADERS,
)

# Add authentication middleware
app.add_middleware(AuthMiddleware, auto_error=False)

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