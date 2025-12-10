"""FastAPI application entry point."""
from fastapi import FastAPI
from contextlib import asynccontextmanager

# Import routers
from app.api import webhooks, rest, health


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifecycle management."""
    # Startup
    print("Starting NexCell AI Receptionist Backend...")
    yield
    # Shutdown
    print("Shutting down NexCell AI Receptionist Backend...")


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="NexCell AI Receptionist API",
        description="AI-powered WhatsApp receptionist for property management",
        version="0.1.0",
        lifespan=lifespan
    )
    
    # Include routers
    app.include_router(health.router, prefix="/health", tags=["health"])
    app.include_router(webhooks.router, prefix="/webhooks", tags=["webhooks"])
    app.include_router(rest.router, prefix="/api", tags=["admin"])
    
    @app.get("/")
    async def root():
        """Root endpoint."""
        return {
            "message": "NexCell AI Receptionist API",
            "version": "0.1.0"
        }
    
    return app


app = create_app()


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
