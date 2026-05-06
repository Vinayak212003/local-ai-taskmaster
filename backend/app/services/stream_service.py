"""
services/stream_service.py — Server-Sent Events (SSE) manager.
Each task gets an async queue. Frontend subscribes per task_id.
"""
import asyncio
import json
import logging
from typing import AsyncGenerator

logger = logging.getLogger(__name__)

# task_id -> asyncio.Queue
_queues: dict[str, asyncio.Queue] = {}


def get_or_create_queue(task_id: str) -> asyncio.Queue:
    if task_id not in _queues:
        _queues[task_id] = asyncio.Queue(maxsize=500)
    return _queues[task_id]


def cleanup_queue(task_id: str):
    _queues.pop(task_id, None)


async def push_event(task_id: str, event_type: str, data: dict | str) -> None:
    """Push an SSE event to the task's queue."""
    q = get_or_create_queue(task_id)
    payload = json.dumps({"type": event_type, "data": data})
    try:
        await q.put(payload)
    except asyncio.QueueFull:
        logger.warning("SSE queue full for task %s", task_id)


async def push_token(task_id: str, agent: str, token: str) -> None:
    """Shortcut: push a streaming token from an agent."""
    await push_event(task_id, "token", {"agent": agent, "token": token})


async def push_status(task_id: str, status: str, message: str = "") -> None:
    await push_event(task_id, "status", {"status": status, "message": message})


async def push_done(task_id: str, result: dict) -> None:
    await push_event(task_id, "done", result)


async def push_error(task_id: str, error: str) -> None:
    await push_event(task_id, "error", {"error": error})


async def stream_task_events(task_id: str) -> AsyncGenerator[str, None]:
    """
    SSE generator for a single task.
    Yields 'data: ...\n\n' formatted SSE strings until DONE or ERROR.
    """
    q = get_or_create_queue(task_id)

    try:
        while True:
            try:
                payload = await asyncio.wait_for(q.get(), timeout=30)
            except asyncio.TimeoutError:
                # Send keepalive comment
                yield ": keepalive\n\n"
                continue

            yield f"data: {payload}\n\n"
            q.task_done()

            # Parse to check if we should stop
            try:
                event = json.loads(payload)
                if event.get("type") in ("done", "error"):
                    break
            except Exception:
                continue
    finally:
        cleanup_queue(task_id)
