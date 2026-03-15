import datetime as dt
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class GoalLevel(str, Enum):
    yearly = "yearly"
    monthly = "monthly"
    weekly = "weekly"


class GoalCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    description: str = Field(default="", max_length=1000)
    category: str = Field(default="personal", max_length=30)
    level: GoalLevel = GoalLevel.monthly
    target_date: dt.date | None = None
    parent_goal_id: UUID | None = None


class GoalUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=2, max_length=200)
    description: str | None = Field(default=None, max_length=1000)
    category: str | None = None
    level: GoalLevel | None = None
    target_date: dt.date | None = None
    status: str | None = None


class GoalResponse(BaseModel):
    id: UUID
    user_id: UUID
    parent_goal_id: UUID | None
    title: str
    description: str
    category: str
    level: str
    target_date: dt.date | None
    progress_percent: float
    status: str
    linked_tasks_total: int
    linked_tasks_done: int
    created_at: dt.datetime

    model_config = {"from_attributes": True}
