"""
services/prompt_service.py — Loads and renders prompt templates from YAML files.
Templates use {variable} substitution for dynamic content injection.
"""
import logging
from pathlib import Path
from string import Template
from typing import Optional

import yaml

from app.core.config import settings

logger = logging.getLogger(__name__)


class PromptService:
    def __init__(self):
        self.prompts_dir = settings.PROMPTS_DIR
        self._cache: dict[str, dict] = {}

    def _load_template(self, name: str) -> dict:
        """Load a YAML prompt template by name (cached)."""
        if name in self._cache:
            return self._cache[name]

        path = self.prompts_dir / f"{name}.yaml"
        if not path.exists():
            raise FileNotFoundError(f"Prompt template not found: {path}")

        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f)

        self._cache[name] = data
        return data

    def render(self, template_name: str, **kwargs) -> tuple[str, Optional[str]]:
        """
        Render a prompt template with given variables.
        Returns (user_prompt, system_prompt) tuple.
        """
        data = self._load_template(template_name)

        user_template = data.get("user", "")
        system_template = data.get("system", "")

        try:
            user_prompt = Template(user_template).safe_substitute(**kwargs)
            system_prompt = Template(system_template).safe_substitute(**kwargs) if system_template else None
        except Exception as e:
            logger.error("Prompt render error for %s: %s", template_name, e)
            user_prompt = user_template
            system_prompt = system_template or None

        return user_prompt, system_prompt

    def list_templates(self) -> list[str]:
        """List available prompt template names."""
        if not self.prompts_dir.exists():
            return []
        return [p.stem for p in self.prompts_dir.glob("*.yaml")]

    def get_raw(self, template_name: str) -> dict:
        """Return raw template data (for UI editing)."""
        return self._load_template(template_name)

    def invalidate_cache(self):
        """Clear template cache (reload from disk on next use)."""
        self._cache.clear()


prompt_service = PromptService()
