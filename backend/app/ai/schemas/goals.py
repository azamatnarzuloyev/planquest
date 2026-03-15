"""Pydantic schemas for AI goal decomposition."""

from pydantic import BaseModel, Field


class DecompTask(BaseModel):
    title: str = Field(..., max_length=100)
    difficulty: str = Field(default="medium", pattern=r"^(trivial|easy|medium|hard|epic)$")
    estimated_minutes: int = Field(default=30, ge=5, le=180)
    day_offset: int = Field(default=1, ge=1, le=7)


class Milestone(BaseModel):
    week: int = Field(..., ge=1, le=52)
    title: str = Field(..., max_length=100)
    tasks: list[DecompTask] = Field(default_factory=list, max_length=7)


class GoalDecomposition(BaseModel):
    goal_title: str = ""
    total_weeks: int = Field(default=4, ge=1, le=52)
    milestones: list[Milestone] = Field(default_factory=list, max_length=12)
    summary: str = Field(default="", max_length=200)
