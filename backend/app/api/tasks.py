import logging
from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from app.agents.orchestrator import orchestrator
from app.core.database import get_db, AsyncSessionLocal
from app.services.stream_service import stream_task_events
from app.services.task_service import task_service
from app.utils.schemas import TaskCreateRequest, TaskListResponse, TaskResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/tasks", tags=["Tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    body: TaskCreateRequest,
    background_tasks: BackgroundTasks,
    db: AsyncSession = Depends(get_db),
):
    task = await task_service.create_task(
        db=db,
        title=body.title,
        description=body.description,
        model=body.model,
    )
    background_tasks.add_task(_run_orchestration, task.id)
    return TaskResponse(**task.to_dict())


async def _run_orchestration(task_id: str):
    async with AsyncSessionLocal() as db:
        try:
            await orchestrator.run(task_id=task_id, db=db)
        except Exception as e:
            logger.exception("Orchestration failed for task %s: %s", task_id, e)


@router.get("", response_model=TaskListResponse)
async def list_tasks(
    limit: int = 50,
    offset: int = 0,
    db: AsyncSession = Depends(get_db),
):
    tasks = await task_service.list_tasks(db, limit=limit, offset=offset)
    return TaskListResponse(
        tasks=[TaskResponse(**t.to_dict()) for t in tasks],
        total=len(tasks),
    )


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return TaskResponse(**task.to_dict())


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(task_id: str, db: AsyncSession = Depends(get_db)):
    deleted = await task_service.delete_task(db, task_id)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")


@router.get("/{task_id}/stream")
async def stream_task(task_id: str, db: AsyncSession = Depends(get_db)):
    task = await task_service.get_task(db, task_id)
    if not task:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")
    return StreamingResponse(
        stream_task_events(task_id),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
            "Connection": "keep-alive",
        },
    )