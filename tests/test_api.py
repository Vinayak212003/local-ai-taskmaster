"""
tests/test_api.py — Integration tests for LocalAI TaskMaster API.
Run: pytest tests/ -v
"""
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport

# Patch DB URL to use in-memory SQLite for tests
import os
os.environ["DATABASE_URL"] = "sqlite+aiosqlite:///:memory:"
os.environ["DATABASE_PATH"] = ":memory:"

from backend.main import app
from backend.app.core.database import init_db


@pytest_asyncio.fixture
async def client():
    await init_db()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest.mark.asyncio
async def test_health(client):
    resp = await client.get("/api/health")
    assert resp.status_code == 200
    data = resp.json()
    assert "status" in data
    assert "ollama_online" in data
    assert "app_version" in data


@pytest.mark.asyncio
async def test_create_task(client):
    resp = await client.post("/api/tasks", json={
        "title": "Test Task",
        "description": "Write a haiku about unit testing in Python",
        "model": "mistral",
    })
    assert resp.status_code == 201
    data = resp.json()
    assert data["title"] == "Test Task"
    assert data["status"] == "pending"
    assert "id" in data


@pytest.mark.asyncio
async def test_list_tasks(client):
    # Create a task first
    await client.post("/api/tasks", json={
        "title": "List Test",
        "description": "A task for testing the list endpoint",
        "model": "mistral",
    })
    resp = await client.get("/api/tasks")
    assert resp.status_code == 200
    data = resp.json()
    assert "tasks" in data
    assert data["total"] >= 1


@pytest.mark.asyncio
async def test_get_task_not_found(client):
    resp = await client.get("/api/tasks/nonexistent-id")
    assert resp.status_code == 404


@pytest.mark.asyncio
async def test_delete_task(client):
    # Create
    create_resp = await client.post("/api/tasks", json={
        "title": "Delete Me",
        "description": "This task will be deleted in the test",
        "model": "mistral",
    })
    task_id = create_resp.json()["id"]

    # Delete
    del_resp = await client.delete(f"/api/tasks/{task_id}")
    assert del_resp.status_code == 204

    # Verify gone
    get_resp = await client.get(f"/api/tasks/{task_id}")
    assert get_resp.status_code == 404


@pytest.mark.asyncio
async def test_create_task_validation(client):
    # Missing required fields
    resp = await client.post("/api/tasks", json={"title": "T"})
    assert resp.status_code == 422

    # Description too short
    resp = await client.post("/api/tasks", json={
        "title": "Valid Title",
        "description": "Short",
    })
    assert resp.status_code == 422
