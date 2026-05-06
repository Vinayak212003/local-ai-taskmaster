"""
tests/test_agents.py — Unit tests for agent logic with mocked Ollama.
"""
import pytest
from unittest.mock import AsyncMock, patch

from backend.app.agents.planner import PlannerAgent
from backend.app.agents.validator import ValidatorAgent


class TestPlannerAgent:
    @pytest.mark.asyncio
    async def test_plan_returns_subtasks(self):
        agent = PlannerAgent()
        mock_response = '["Research the topic", "Write an outline", "Draft the content", "Review and edit"]'

        tokens = iter(mock_response)

        async def mock_stream(*args, **kwargs):
            for c in mock_response:
                yield c

        with patch("backend.app.agents.planner.ollama_client") as mock_client:
            mock_client.generate_stream = mock_stream
            plan_text, subtasks = await agent.plan("Write a blog post about Python")

        assert len(subtasks) == 4
        assert "Research the topic" in subtasks

    def test_parse_subtasks_valid_json(self):
        agent = PlannerAgent()
        raw = '["Task 1", "Task 2", "Task 3"]'
        result = agent._parse_subtasks(raw)
        assert result == ["Task 1", "Task 2", "Task 3"]

    def test_parse_subtasks_with_markdown_fence(self):
        agent = PlannerAgent()
        raw = '```json\n["Task A", "Task B"]\n```'
        result = agent._parse_subtasks(raw)
        assert result == ["Task A", "Task B"]

    def test_parse_subtasks_invalid_json_returns_empty(self):
        agent = PlannerAgent()
        result = agent._parse_subtasks("This is not JSON at all.")
        assert result == []


class TestValidatorAgent:
    def test_parse_validation_valid_json(self):
        agent = ValidatorAgent()
        raw = '{"score": 85, "quality": "good", "summary": "Good work.", "feedback": "Clear output.", "improvements": "Add examples."}'
        result = agent._parse_validation(raw)
        assert result["score"] == 85
        assert result["quality"] == "good"

    def test_parse_validation_fallback_extracts_score(self):
        agent = ValidatorAgent()
        raw = 'The task was completed. "score": 72 was my assessment.'
        result = agent._parse_validation(raw)
        assert result["score"] == 72

    def test_parse_validation_total_failure_returns_defaults(self):
        agent = ValidatorAgent()
        result = agent._parse_validation("garbage input ###")
        assert isinstance(result["score"], int)
        assert "quality" in result
