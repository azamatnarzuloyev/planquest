"""Pydantic schemas for AI-generated plans."""

from pydantic import BaseModel, Field


class TimeBlock(BaseModel):
    start: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    end: str = Field(..., pattern=r"^\d{2}:\d{2}$")
    type: str = Field(..., pattern=r"^(task|habit|focus_session|break)$")
    ref_id: str | None = None
    title: str = Field(..., max_length=100)
    mode: str | None = None


class SuggestedTask(BaseModel):
    title: str = Field(..., max_length=100)
    priority: str = Field(default="medium", pattern=r"^(low|medium|high|critical)$")
    difficulty: str = Field(default="medium", pattern=r"^(trivial|easy|medium|hard|epic)$")
    estimated_minutes: int = Field(default=30, ge=5, le=180)


class DailyPlan(BaseModel):
    plan_type: str = "daily"
    date: str = ""
    time_blocks: list[TimeBlock] = Field(default_factory=list, max_length=20)
    suggested_new_tasks: list[SuggestedTask] = Field(default_factory=list, max_length=3)
    coaching_note: str = Field(default="", max_length=200)
