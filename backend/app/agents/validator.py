"""
agents/validator.py — Validator Agent
Reviews all executor outputs and provides a quality score + feedback.
Also synthesizes a final consolidated result.
"""
import json
import logging
import re
from typing import Optional

from app.core.config import settings
from app.services.ollama_client import ollama_client

logger = logging.getLogger(__name__)

VALIDATOR_SYSTEM = """You are a quality assurance AI. You review the output of an AI task pipeline
and provide structured feedback.

You MUST respond in valid JSON only. No preamble. No markdown fences.

JSON schema:
{
  "score": <integer 0-100>,
  "quality": "<poor|fair|good|excellent>",
  "summary": "<2-3 sentence synthesis of all outputs into final result>",
  "feedback": "<1-2 sentences on what was done well>",
  "improvements": "<1-2 sentences on what could be better>"
}"""

VALIDATOR_USER = """Original Task:
{original_task}

Subtask Results:
{subtask_results}

Evaluate the quality of the above results and provide a final synthesis."""


class ValidatorAgent:
    """
    Validates and scores the pipeline output.
    Returns structured quality assessment.
    """

    async def validate(
        self,
        original_task: str,
        subtask_results: list[tuple[str, str]],
        model: Optional[str] = None,
        stream_callback=None,
    ) -> dict:
        """
        Validate all subtask outputs.

        Returns:
            {score, quality, summary, feedback, improvements}
        """
        model = model or settings.OLLAMA_MODEL

        # Build compact results summary (limit tokens)
        formatted_results = ""
        for i, (desc, result) in enumerate(subtask_results):
            formatted_results += f"\n[Subtask {i+1}]: {desc}\n{result[:600]}\n---"

        user_prompt = VALIDATOR_USER.format(
            original_task=original_task[:300],
            subtask_results=formatted_results[:3000],  # cap total input
        )

        logger.info("Validator: evaluating %d subtask results", len(subtask_results))

        full_response = ""
        try:
            async for token in ollama_client.generate_stream(
                prompt=user_prompt,
                system=VALIDATOR_SYSTEM,
                model=model,
                max_tokens=settings.VALIDATOR_MAX_TOKENS,
                temperature=0.1,  # very deterministic for scoring
            ):
                full_response += token
                if stream_callback:
                    await stream_callback(token)
        except RuntimeError as e:
            logger.error("Validator error: %s", e)
            raise

        result = self._parse_validation(full_response)
        logger.info("Validator: score=%s, quality=%s", result.get("score"), result.get("quality"))
        return result

    def _parse_validation(self, raw: str) -> dict:
        """Parse JSON from validator output."""
        # Strip markdown fences
        raw = re.sub(r"```(?:json)?", "", raw).strip()

        # Find JSON object
        match = re.search(r"\{.*\}", raw, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(0))
            except json.JSONDecodeError as e:
                logger.error("Validator JSON parse error: %s", e)

        # Fallback: extract score with regex
        score_match = re.search(r'"score"\s*:\s*(\d+)', raw)
        score = int(score_match.group(1)) if score_match else 50

        return {
            "score": score,
            "quality": "fair",
            "summary": raw[:500] if raw else "Task completed.",
            "feedback": "Results generated successfully.",
            "improvements": "Output parsing encountered issues.",
        }


validator_agent = ValidatorAgent()
