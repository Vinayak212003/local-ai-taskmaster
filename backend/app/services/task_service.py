"""
services/task_service.py — Business logic for Task CRUD operations.
All DB interactions go through this service layer.
"""
import logging
from datetime import datetime
from typing import Optional

from sqlalchemy import select, desc
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.task import Task, SubTask, TaskStatus

logger = logging.getLogger(__name__)


class TaskService:

    async def create_task(
        self,
        db: AsyncSession,
        title: str,
        description: str,
        model: str = "mistral",
    ) -> Task:
        task = Task(
            title=title,
            description=description,
            model=model,
            status=TaskStatus.PENDING,
        )
        db.add(task)
        await db.commit()
        await db.refresh(task)
        logger.info("Created task %s: %s", task.id, task.title)
        return task

    async def get_task(self, db: AsyncSession, task_id: str) -> Optional[Task]:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.subtasks))
            .where(Task.id == task_id)
        )
        return result.scalar_one_or_none()

    async def list_tasks(
        self, db: AsyncSession, limit: int = 50, offset: int = 0
    ) -> list[Task]:
        result = await db.execute(
            select(Task)
            .options(selectinload(Task.subtasks))
            .order_by(desc(Task.created_at))
            .limit(limit)
            .offset(offset)
        )
        return list(result.scalars().all())

    async def update_status(
        self, db: AsyncSession, task_id: str, status: TaskStatus
    ) -> None:
        task = await self.get_task(db, task_id)
        if task:
            task.status = status
            task.updated_at = datetime.utcnow()
            if status == TaskStatus.COMPLETE:
                task.completed_at = datetime.utcnow()
            await db.commit()

    async def save_plan(
        self, db: AsyncSession, task_id: str, plan_text: str, subtask_descriptions: list[str]
    ) -> list[SubTask]:
        task = await self.get_task(db, task_id)
        if not task:
            raise ValueError(f"Task {task_id} not found")

        task.plan_output = plan_text
        task.status = TaskStatus.EXECUTING

        subtasks = []
        for i, desc_text in enumerate(subtask_descriptions):
            st = SubTask(
                task_id=task_id,
                order_index=i,
                description=desc_text,
                status="pending",
            )
            db.add(st)
            subtasks.append(st)

        await db.commit()
        return subtasks

    async def save_subtask_result(
        self, db: AsyncSession, subtask_id: str, result: str
    ) -> None:
        result_obj = await db.get(SubTask, subtask_id)
        if result_obj:
            result_obj.result = result
            result_obj.status = "complete"
            await db.commit()

    async def save_final_result(
        self,
        db: AsyncSession,
        task_id: str,
        final_result: str,
        validation_score: float,
        validation_feedback: str,
    ) -> None:
        task = await self.get_task(db, task_id)
        if task:
            task.final_result = final_result
            task.validation_score = validation_score
            task.validation_feedback = validation_feedback
            task.status = TaskStatus.COMPLETE
            task.completed_at = datetime.utcnow()
            await db.commit()

    async def mark_failed(
        self, db: AsyncSession, task_id: str, error: str
    ) -> None:
        task = await self.get_task(db, task_id)
        if task:
            task.status = TaskStatus.FAILED
            task.error_message = error
            await db.commit()

    async def delete_task(self, db: AsyncSession, task_id: str) -> bool:
        task = await self.get_task(db, task_id)
        if task:
            await db.delete(task)
            await db.commit()
            return True
        return False


task_service = TaskService()
