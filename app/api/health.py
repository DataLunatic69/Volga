"""Health check endpoints."""
from fastapi import APIRouter
from typing import Dict, Any

router = APIRouter()


@router.get("/")
async def health_check() -> Dict[str, Any]:
    """Application health check.
    
    Returns:
        Health status.
    """
    return {
        "status": "healthy",
        "service": "NexCell AI Receptionist",
        "version": "0.1.0"
    }


@router.get("/ready")
async def readiness_check() -> Dict[str, Any]:
    """Application readiness check.
    
    Returns:
        Readiness status and dependencies.
    """
    # TODO: Check dependencies (DB, Redis, Vector DB, LLM)
    return {
        "ready": True,
        "dependencies": {
            "database": "connected",
            "redis": "connected",
            "vector_db": "connected",
            "llm": "connected"
        }
    }
