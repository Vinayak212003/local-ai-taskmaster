"""
api/health.py — System health and Ollama status endpoints.
"""
from fastapi import APIRouter

from app.core.config import settings
from app.services.ollama_client import ollama_client
from app.utils.schemas import HealthResponse

router = APIRouter(prefix="/api", tags=["Health"])


@router.get("/health", response_model=HealthResponse)
async def health_check():
    """Check API + Ollama connectivity."""
    ollama_ok = await ollama_client.health_check()
    models = await ollama_client.list_models() if ollama_ok else []

    return HealthResponse(
        status="ok" if ollama_ok else "degraded",
        ollama_online=ollama_ok,
        ollama_url=settings.OLLAMA_BASE_URL,
        available_models=models,
        app_version=settings.APP_VERSION,
    )
