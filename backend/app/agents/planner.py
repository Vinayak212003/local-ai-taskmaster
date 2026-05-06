"""
agents/planner.py — Planner Agent
Decomposes a high-level task description into ordered subtasks.
Output is a structured JSON list of subtask descriptions.
"""
import json
import logging
import re
from typing import Optional

from app.core.config import settings
from app.services.ollama_client import ollama_client
from app.services.prompt_service import prompt_service

logger = logging.getLogger(__name__)

PLANNER_SYSTEM = """You are a precise task planning AI. Your job is to decompose a user's task
into a clear, ordered list of subtasks. Each subtask must be specific and actionable.

RULES:
- Output ONLY a valid JSON array of strings. No preamble, no explanation.
- Maximum {max_subtasks} subtasks.
- Each subtask must be 1-2 sentences, clear and self-contained.
- Order subtasks logically (dependencies first).

Example output:
["Research the topic and gather key facts", "Outline the main sections", "Write the introduction", "Write the body content", "Write the conclusion and review"]
"""

PLANNER_USER = """Task to decompose:
{task_description}

Return ONLY a JSON array of subtask strings. No other text."""


class PlannerAgent:
    """
    Breaks a task into subtasks using local LLM.
    Returns: (plan_text: str, subtasks: list[str])
    """

    async def plan(
        self,
        task_description: str,
        model: Optional[str] = None,
        stream_callback=None,
    ) -> tuple[str, list[str]]:
        """
        Generate a plan for the given task.

        Args:
            task_description: Raw task from user.
            model: Override model.
            stream_callback: async callable(token: str) for streaming.

        Returns:
            (raw_plan_text, list_of_subtask_strings)
        """
        model = model or settings.OLLAMA_MODEL

        system_prompt = PLANNER_SYSTEM.format(max_subtasks=settings.MAX_SUBTASKS)
        user_prompt = PLANNER_USER.format(task_description=task_description)

        logger.info("Planner: generating plan for task (model=%s)", model)

        # Stream tokens while collecting full response
        full_response = ""
        try:
            async for token in ollama_client.generate_stream(
                prompt=user_prompt,
                system=system_prompt,
                model=model,
                max_tokens=settings.PLANNER_MAX_TOKENS,
                temperature=0.2,  # low temp for structured output
            ):
                full_response += token
                if stream_callback:
                    await stream_callback(token)
        except RuntimeError as e:
            logger.error("Planner stream error: %s", e)
            raise

        # Parse JSON subtask list from response
        subtasks = self._parse_subtasks(full_response)

        if not subtasks:
            logger.warning("Planner: no subtasks parsed, using fallback")
            subtasks = [f"Complete the task: {task_description[:200]}"]

        logger.info("Planner: generated %d subtasks", len(subtasks))
        return full_response, subtasks

    def _parse_subtasks(self, raw: str) -> list[str]:
        """Extract JSON array from raw LLM output (handles markdown fences)."""
        # Strip markdown code fences if present
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        # Find first [ ... ] block
        match = re.search(r"\[.*\]", raw, re.DOTALL)
        if not match:
            return []

        try:
            parsed = json.loads(match.group(0))
            if isinstance(parsed, list):
                return [str(s).strip() for s in parsed if str(s).strip()]
        except json.JSONDecodeError as e:
            logger.error("Planner JSON parse error: %s | raw: %s", e, raw[:200])

        return []


planner_agent = PlannerAgent()
