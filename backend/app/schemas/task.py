from datetime import date, datetime
from enum import Enum
from uuid import UUID

from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"
    critical = "critical"


class TaskDifficulty(str, Enum):
    trivial = "trivial"
    easy = "easy"
    medium = "medium"
    hard = "hard"
    epic = "epic"


class TaskStatus(str, Enum):
    pending = "pending"
    completed = "completed"
    skipped = "skipped"
    archived = "archived"


class TaskSource(str, Enum):
    bot = "bot"
    mini_app = "mini_app"
    ai_plan = "ai_plan"


class TaskCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    notes: str | None = Field(default=None, max_length=2000)
    planned_date: date
    due_date: date | None = None
    priority: TaskPriority = TaskPriority.medium
    difficulty: TaskDifficulty = TaskDifficulty.medium
    estimated_minutes: int | None = Field(default=None, ge=1, le=480)
    category: str | None = Field(default=None, max_length=50)
    source: TaskSource = TaskSource.mini_app


class TaskUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    notes: str | None = None
    planned_date: date | None = None
    due_date: date | None = None
    priority: TaskPriority | None = None
    difficulty: TaskDifficulty | None = None
    estimated_minutes: int | None = Field(default=None, ge=1, le=480)
    category: str | None = None
    status: TaskStatus | None = None


class TaskResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    notes: str | None
    planned_date: date
    due_date: date | None
    priority: str
    difficulty: str
    estimated_minutes: int | None
    category: str | None
    goal_id: UUID | None
    status: str
    source: str
    recurrence_rule: str | None
    completed_at: datetime | None
    xp_awarded: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
