import datetime as dt
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class HabitType(str, Enum):
    yes_no = "yes_no"
    count = "count"
    duration = "duration"
    avoid = "avoid"


class HabitFrequency(str, Enum):
    daily = "daily"
    weekdays = "weekdays"
    weekly = "weekly"
    custom = "custom"


# === Habit CRUD ===


class HabitCreate(BaseModel):
    title: str = Field(min_length=2, max_length=200)
    type: HabitType
    target_value: int = Field(default=1, ge=1)
    frequency: HabitFrequency = HabitFrequency.daily
    frequency_days: Optional[list[int]] = None
    reminder_time: Optional[dt.time] = None
    icon: str = Field(default="✅", max_length=10)
    color: str = Field(default="#4CAF50", max_length=10)


class HabitUpdate(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=200)
    target_value: Optional[int] = Field(default=None, ge=1)
    frequency: Optional[HabitFrequency] = None
    frequency_days: Optional[list[int]] = None
    reminder_time: Optional[dt.time] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    status: Optional[str] = None


class HabitResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    type: str
    target_value: int
    frequency: str
    frequency_days: Optional[list[int]]
    reminder_time: Optional[dt.time]
    icon: str
    color: str
    status: str
    created_at: dt.datetime
    updated_at: dt.datetime

    model_config = {"from_attributes": True}


# === Habit Log ===


class HabitLogCreate(BaseModel):
    value: int = Field(default=1, ge=0)
    log_date: Optional[dt.date] = None  # defaults to today
    source: str = "mini_app"


class HabitLogResponse(BaseModel):
    id: UUID
    habit_id: UUID
    date: dt.date
    value: int
    completed: bool
    logged_at: dt.datetime
    source: str
    xp_awarded: int = 0

    model_config = {"from_attributes": True}


class HabitWithLogResponse(BaseModel):
    habit: HabitResponse
    today_log: Optional[HabitLogResponse] = None
    current_streak: int = 0
