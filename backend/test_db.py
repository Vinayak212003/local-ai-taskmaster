import asyncio
from app.core.database import AsyncSessionLocal, init_db
from app.services.task_service import task_service

async def test():
    await init_db()
    async with AsyncSessionLocal() as db:
        task = await task_service.create_task(db, 'Test', 'Write a short poem about Python', 'mistral')
        print('SUCCESS - Task created:', task.id)

asyncio.run(test())