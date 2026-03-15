"""User context schemas for AI agents."""

from pydantic import BaseModel


class TaskContext(BaseModel):
    id: str
    title: str
    priority: str
    difficulty: str
    estimated_minutes: int | None = None
    planned_date: str
    category: str | None = None


class HabitContext(BaseModel):
    id: str
    title: str
    type: str
    target_value: int
    today_completed: bool = False
    current_streak: int = 0


class UserContext(BaseModel):
    segment: str | None = None
    timezone: str = "UTC"
    today_date: str = ""
    day_of_week: str = ""

    # Tasks
    pending_tasks: list[TaskContext] = []
    overdue_tasks: list[TaskContext] = []
    completed_today: int = 0

    # Habits
    habits: list[HabitContext] = []
    habits_done_today: int = 0

    # Stats
    streak_current: int = 0
    streak_best: int = 0
    focus_today_minutes: int = 0
    avg_tasks_per_day: float = 0
    avg_focus_per_day: float = 0

    # Level
    current_level: int = 1
    total_xp: int = 0
