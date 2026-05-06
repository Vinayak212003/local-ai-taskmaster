"""
utils/schemas.py — Pydantic v2 request/response schemas for all API endpoints.
"""
from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


# ── Task Schemas ──────────────────────────────────────────────────────────────

class TaskCreateRequest(BaseModel):
    title: str = Field(..., min_length=3, max_length=255, description="Short task title")
    description: str = Field(..., min_length=10, description="Full task description")
    model: str = Field(default="mistral", description="Ollama model to use")


class SubTaskResponse(BaseModel):
    id: str
    task_id: str
    order_index: int
    description: str
    result: Optional[str] = None
    status: str

    class Config:
        from_attributes = True


class TaskResponse(BaseModel):
    id: str
    title: str
    description: str
    status: str
    model: str
    plan_output: Optional[str] = None
    final_result: Optional[str] = None
    validation_score: Optional[float] = None
    validation_feedback: Optional[str] = None
    error_message: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    subtasks: list[SubTaskResponse] = []

    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    tasks: list[TaskResponse]
    total: int


# ── Health Schemas ─────────────────────────────────────────────────────────────

class HealthResponse(BaseModel):
    status: str
    ollama_online: bool
    ollama_url: str
    available_models: list[str]
    app_version: str


# ── Prompt Schemas ─────────────────────────────────────────────────────────────

class PromptTemplateResponse(BaseModel):
    name: str
    system: Optional[str] = None
    user: str


class ErrorResponse(BaseModel):
    detail: str
    code: Optional[str] = None
