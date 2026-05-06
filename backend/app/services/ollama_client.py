"""
services/ollama_client.py — Async Ollama API client
Supports streaming and non-streaming inference.
Handles connection errors gracefully.
"""
import json
import logging
from typing import AsyncGenerator, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class OllamaClient:
    """Lightweight async client for Ollama local inference."""

    def __init__(self):
        self.base_url = settings.OLLAMA_BASE_URL
        self.default_model = settings.OLLAMA_MODEL
        self.timeout = settings.OLLAMA_TIMEOUT

    async def health_check(self) -> bool:
        """Return True if Ollama is reachable."""
        try:
            async with httpx.AsyncClient(timeout=5) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                return resp.status_code == 200
        except Exception:
            return False

    async def list_models(self) -> list[str]:
        """Return list of locally available models."""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                resp = await client.get(f"{self.base_url}/api/tags")
                resp.raise_for_status()
                data = resp.json()
                return [m["name"] for m in data.get("models", [])]
        except Exception as e:
            logger.error("Failed to list models: %s", e)
            return []

    async def generate(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.3,
    ) -> str:
        """Non-streaming generate — waits for full response."""
        model = model or self.default_model
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": False,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "num_ctx": settings.OLLAMA_NUM_CTX,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                resp = await client.post(
                    f"{self.base_url}/api/generate",
                    json=payload,
                )
                resp.raise_for_status()
                data = resp.json()
                return data.get("response", "").strip()
        except httpx.ConnectError:
            raise RuntimeError(
                "Cannot connect to Ollama. Is it running? Run: ollama serve"
            )
        except httpx.TimeoutException:
            raise RuntimeError(
                f"Ollama timeout after {self.timeout}s. Try a smaller model."
            )
        except Exception as e:
            logger.error("Ollama generate error: %s", e)
            raise RuntimeError(f"Ollama error: {str(e)}")

    async def generate_stream(
        self,
        prompt: str,
        model: Optional[str] = None,
        system: Optional[str] = None,
        max_tokens: int = 1000,
        temperature: float = 0.3,
    ) -> AsyncGenerator[str, None]:
        """Streaming generate — yields text chunks as they arrive."""
        model = model or self.default_model
        payload = {
            "model": model,
            "prompt": prompt,
            "stream": True,
            "options": {
                "num_predict": max_tokens,
                "temperature": temperature,
                "num_ctx": settings.OLLAMA_NUM_CTX,
            },
        }
        if system:
            payload["system"] = system

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                async with client.stream(
                    "POST",
                    f"{self.base_url}/api/generate",
                    json=payload,
                ) as resp:
                    resp.raise_for_status()
                    async for line in resp.aiter_lines():
                        if not line.strip():
                            continue
                        try:
                            chunk = json.loads(line)
                            token = chunk.get("response", "")
                            if token:
                                yield token
                            if chunk.get("done", False):
                                break
                        except json.JSONDecodeError:
                            continue
        except httpx.ConnectError:
            raise RuntimeError("Cannot connect to Ollama. Run: ollama serve")
        except Exception as e:
            logger.error("Ollama stream error: %s", e)
            raise RuntimeError(f"Ollama streaming error: {str(e)}")


# Singleton
ollama_client = OllamaClient()
