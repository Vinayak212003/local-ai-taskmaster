"""
core/config.py — Centralized configuration management
Loads from environment variables with sensible local defaults.
"""
import os
from pathlib import Path
from pydantic_settings import BaseSettings


BASE_DIR = Path(__file__).resolve().parent.parent.parent


class Settings(BaseSettings):
    # App
    APP_NAME: str = "LocalAI TaskMaster"
    APP_VERSION: str = "1.0.0"
    DEBUG: bool = True
    HOST: str = "0.0.0.0"
    PORT: int = 8000

    # Ollama
    OLLAMA_BASE_URL: str = "http://localhost:11434"
    OLLAMA_MODEL: str = "mistral"
    OLLAMA_TIMEOUT: int = 120  # seconds
    OLLAMA_NUM_CTX: int = 4096  # context window — keep low for 8GB RAM

    # SQLite
    DATABASE_URL: str = f"sqlite+aiosqlite:///{BASE_DIR}/database/taskmaster.db"
    DATABASE_PATH: Path = BASE_DIR / "database" / "taskmaster.db"

    # Prompts
    PROMPTS_DIR: Path = BASE_DIR / "backend" / "config" / "prompts"

    # Agent settings
    MAX_SUBTASKS: int = 8          # limit planner output
    EXECUTOR_MAX_TOKENS: int = 1500
    PLANNER_MAX_TOKENS: int = 800
    VALIDATOR_MAX_TOKENS: int = 600

    # Streaming
    STREAM_HEARTBEAT_INTERVAL: int = 15  # SSE keepalive seconds

    class Config:
        env_file = BASE_DIR / ".env"
        env_file_encoding = "utf-8"


settings = Settings()
