import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import Column, String, Text, DateTime, Float, Integer, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


def new_uuid() -> str:
    return str(uuid.uuid4())


def now():
    return datetime.utcnow()


class TaskStatus(str, PyEnum):
    PENDING = "pending"
    PLANNING = "planning"
    EXECUTING = "executing"
    VALIDATING = "validating"
    COMPLETE = "complete"
    FAILED = "failed"


class Task(Base):
    __tablename__ = "tasks"

    id = Column(String, primary_key=True, default=new_uuid)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String(50), default="pending", nullable=False)
    model = Column(String(100), default="mistral")

    plan_output = Column(Text, nullable=True)
    final_result = Column(Text, nullable=True)
    validation_score = Column(Float, nullable=True)
    validation_feedback = Column(Text, nullable=True)
    error_message = Column(Text, nullable=True)

    created_at = Column(DateTime, default=now)
    updated_at = Column(DateTime, default=now)
    completed_at = Column(DateTime, nullable=True)

    subtasks = relationship("SubTask", back_populates="task", cascade="all, delete-orphan", lazy="selectin")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "status": self.status,
            "model": self.model,
            "plan_output": self.plan_output,
            "final_result": self.final_result,
            "validation_score": self.validation_score,
            "validation_feedback": self.validation_feedback,
            "error_message": self.error_message,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "subtasks": [],
        }


class SubTask(Base):
    __tablename__ = "subtasks"

    id = Column(String, primary_key=True, default=new_uuid)
    task_id = Column(String, ForeignKey("tasks.id"), nullable=False)
    order_index = Column(Integer, nullable=False)
    description = Column(Text, nullable=False)
    result = Column(Text, nullable=True)
    status = Column(String(50), default="pending")
    created_at = Column(DateTime, default=now)

    task = relationship("Task", back_populates="subtasks")

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "task_id": self.task_id,
            "order_index": self.order_index,
            "description": self.description,
            "result": self.result,
            "status": self.status,
        }