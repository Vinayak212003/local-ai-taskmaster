"""
agents/orchestrator.py — Multi-Agent Pipeline Orchestrator
Controls the Planner → Executor → Validator pipeline.
Pushes real-time SSE events for each stage.
"""
import asyncio
import logging

from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.planner import planner_agent
from app.agents.executor import executor_agent
from app.agents.validator import validator_agent
from app.models.task import TaskStatus
from app.services.task_service import task_service
from app.services.stream_service import (
    push_status, push_token, push_done, push_error
)

logger = logging.getLogger(__name__)


class Orchestrator:
    """
    Coordinates the three agents for a given task.
    All LLM calls are streamed; events are pushed to SSE queues.
    """

    async def run(self, task_id: str, db: AsyncSession) -> None:
        """
        Main orchestration pipeline.
        Called as a background task — does NOT raise (logs errors).
        """
        task = await task_service.get_task(db, task_id)
        if not task:
            logger.error("Orchestrator: task %s not found", task_id)
            return

        logger.info("Orchestrator: starting pipeline for task %s", task_id)

        try:
            # ── PHASE 1: PLANNING ──────────────────────────────────────────
            await task_service.update_status(db, task_id, TaskStatus.PLANNING)
            await push_status(task_id, "planning", "🧠 Planner is breaking down your task...")

            plan_tokens = []

            async def on_plan_token(token: str):
                plan_tokens.append(token)
                await push_token(task_id, "planner", token)

            plan_text, subtask_descriptions = await planner_agent.plan(
                task_description=task.description,
                model=task.model,
                stream_callback=on_plan_token,
            )

            # Persist plan + subtasks
            subtasks = await task_service.save_plan(
                db, task_id, plan_text, subtask_descriptions
            )
            await push_status(
                task_id,
                "plan_complete",
                f"✅ Plan ready: {len(subtasks)} subtasks identified",
            )

            # ── PHASE 2: EXECUTION ─────────────────────────────────────────
            await task_service.update_status(db, task_id, TaskStatus.EXECUTING)

            all_results: list[tuple[str, str]] = []

            for i, (subtask_db, subtask_desc) in enumerate(
                zip(subtasks, subtask_descriptions)
            ):
                await push_status(
                    task_id,
                    "executing",
                    f"⚙️ Executing subtask {i+1}/{len(subtasks)}: {subtask_desc[:80]}...",
                )

                subtask_tokens = []

                async def on_exec_token(token: str):
                    subtask_tokens.append(token)
                    await push_token(task_id, f"executor_{i}", token)

                result = await executor_agent.execute_subtask(
                    subtask_description=subtask_desc,
                    parent_task=task.description,
                    model=task.model,
                    stream_callback=on_exec_token,
                )

                # Persist subtask result
                await task_service.save_subtask_result(db, subtask_db.id, result)
                all_results.append((subtask_desc, result))

                await push_status(
                    task_id,
                    "subtask_done",
                    f"✅ Subtask {i+1} complete",
                )

                # Small pause to prevent thermal throttling on low-end machines
                await asyncio.sleep(0.1)

            # ── PHASE 3: VALIDATION ────────────────────────────────────────
            await task_service.update_status(db, task_id, TaskStatus.VALIDATING)
            await push_status(task_id, "validating", "🔍 Validator is reviewing results...")

            async def on_val_token(token: str):
                await push_token(task_id, "validator", token)

            validation = await validator_agent.validate(
                original_task=task.description,
                subtask_results=all_results,
                model=task.model,
                stream_callback=on_val_token,
            )

            # Build consolidated final result
            final_result = self._build_final_result(task.description, all_results, validation)

            await task_service.save_final_result(
                db=db,
                task_id=task_id,
                final_result=final_result,
                validation_score=float(validation.get("score", 0)),
                validation_feedback=validation.get("feedback", ""),
            )

            # ── DONE ───────────────────────────────────────────────────────
            await push_done(task_id, {
                "task_id": task_id,
                "final_result": final_result,
                "validation": validation,
                "subtask_count": len(subtasks),
            })
            logger.info(
                "Orchestrator: task %s complete. Score: %s",
                task_id,
                validation.get("score"),
            )

        except RuntimeError as e:
            # LLM / connectivity error
            error_msg = str(e)
            logger.error("Orchestrator: task %s FAILED: %s", task_id, error_msg)
            await task_service.mark_failed(db, task_id, error_msg)
            await push_error(task_id, error_msg)

        except Exception as e:
            error_msg = f"Unexpected error: {str(e)}"
            logger.exception("Orchestrator: unexpected error for task %s", task_id)
            await task_service.mark_failed(db, task_id, error_msg)
            await push_error(task_id, error_msg)

    def _build_final_result(
        self,
        original_task: str,
        results: list[tuple[str, str]],
        validation: dict,
    ) -> str:
        """Assemble a clean final markdown document."""
        lines = [
            f"# Task Result\n",
            f"**Original Task:** {original_task}\n",
            f"---\n",
            f"## Summary\n",
            f"{validation.get('summary', '')}\n",
            f"---\n",
            f"## Detailed Results\n",
        ]
        for i, (desc, result) in enumerate(results):
            lines.append(f"### Step {i+1}: {desc}\n")
            lines.append(f"{result}\n\n")

        lines += [
            f"---\n",
            f"## Quality Assessment\n",
            f"- **Score:** {validation.get('score', 'N/A')}/100\n",
            f"- **Quality:** {validation.get('quality', 'N/A')}\n",
            f"- **Feedback:** {validation.get('feedback', '')}\n",
            f"- **Improvements:** {validation.get('improvements', '')}\n",
        ]

        return "".join(lines)


orchestrator = Orchestrator()
