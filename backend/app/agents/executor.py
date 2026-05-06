"""
agents/executor.py — Executor Agent
Processes each subtask and produces a detailed result.
Runs subtasks sequentially to stay within 8GB RAM.
"""
import logging
from typing import Optional

from app.core.config import settings
from app.services.ollama_client import ollama_client

logger = logging.getLogger(__name__)

EXECUTOR_SYSTEM = """You are a skilled AI assistant that executes specific tasks with precision.
You will receive a subtask that is part of a larger goal.

RULES:
- Provide a thorough, high-quality response for ONLY the given subtask.
- Be concise but complete. Avoid filler or repetition.
- Format output in markdown for readability.
- Do not ask clarifying questions — make reasonable assumptions."""

EXECUTOR_USER = """Parent Task Context:
{parent_task}

Your current subtask to execute:
{subtask_description}

Execute this subtask completely and provide your result:"""


class ExecutorAgent:
    """
    Executes individual subtasks using the local LLM.
    Returns: result string per subtask.
    """

    async def execute_subtask(
        self,
        subtask_description: str,
        parent_task: str,
        model: Optional[str] = None,
        stream_callback=None,
    ) -> str:
        """
        Execute a single subtask.

        Args:
            subtask_description: The specific subtask to perform.
            parent_task: The overall task context.
            model: Override model.
            stream_callback: async callable(token: str).

        Returns:
            Full result string.
        """
        model = model or settings.OLLAMA_MODEL

        user_prompt = EXECUTOR_USER.format(
            parent_task=parent_task[:500],  # limit context size
            subtask_description=subtask_description,
        )

        logger.info("Executor: executing subtask: %s...", subtask_description[:80])

        full_result = ""
        try:
            async for token in ollama_client.generate_stream(
                prompt=user_prompt,
                system=EXECUTOR_SYSTEM,
                model=model,
                max_tokens=settings.EXECUTOR_MAX_TOKENS,
                temperature=0.5,
            ):
                full_result += token
                if stream_callback:
                    await stream_callback(token)
        except RuntimeError as e:
            logger.error("Executor error on subtask: %s", e)
            raise

        logger.info("Executor: subtask complete (%d chars)", len(full_result))
        return full_result.strip()

    async def execute_all(
        self,
        subtasks: list[str],
        parent_task: str,
        model: Optional[str] = None,
        subtask_start_callback=None,
        stream_callback=None,
    ) -> list[tuple[str, str]]:
        """
        Execute all subtasks sequentially.

        Returns:
            List of (subtask_description, result) tuples.
        """
        results = []
        for i, subtask_desc in enumerate(subtasks):
            logger.info("Executor: starting subtask %d/%d", i + 1, len(subtasks))

            if subtask_start_callback:
                await subtask_start_callback(i, subtask_desc)

            result = await self.execute_subtask(
                subtask_description=subtask_desc,
                parent_task=parent_task,
                model=model,
                stream_callback=stream_callback,
            )
            results.append((subtask_desc, result))

        return results


executor_agent = ExecutorAgent()
