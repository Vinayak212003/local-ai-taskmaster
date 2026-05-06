"""
api/prompts.py — Prompt template management endpoints.
"""
from fastapi import APIRouter, HTTPException
from app.services.prompt_service import prompt_service
from app.utils.schemas import PromptTemplateResponse

router = APIRouter(prefix="/api/prompts", tags=["Prompts"])


@router.get("", response_model=list[str])
async def list_prompts():
    """List all available prompt template names."""
    return prompt_service.list_templates()


@router.get("/{name}", response_model=PromptTemplateResponse)
async def get_prompt(name: str):
    """Get a specific prompt template by name."""
    try:
        data = prompt_service.get_raw(name)
        return PromptTemplateResponse(
            name=name,
            system=data.get("system"),
            user=data.get("user", ""),
        )
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=f"Prompt '{name}' not found")


@router.post("/reload", status_code=204)
async def reload_prompts():
    """Invalidate prompt cache — reloads templates from disk."""
    prompt_service.invalidate_cache()
