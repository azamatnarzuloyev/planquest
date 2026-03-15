import datetime as dt
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, Field


class FocusMode(str, Enum):
    pomodoro_25 = "pomodoro_25"
    deep_50 = "deep_50"
    ultra_90 = "ultra_90"
    custom = "custom"


class FocusStartRequest(BaseModel):
    mode: FocusMode = FocusMode.pomodoro_25
    planned_duration: Optional[int] = Field(default=None, ge=5, le=180)  # only for custom
    task_id: Optional[UUID] = None


class FocusSessionResponse(BaseModel):
    id: UUID
    user_id: UUID
    task_id: Optional[UUID]
    planned_duration: int
    actual_duration: int
    mode: str
    status: str
    started_at: dt.datetime
    ended_at: Optional[dt.datetime]
    xp_awarded: int

    model_config = {"from_attributes": True}


class FocusEndResponse(BaseModel):
    session: FocusSessionResponse
    xp_awarded: int
    total_xp: int
    leveled_up: bool
    new_level: int


class FocusStatsResponse(BaseModel):
    today_minutes: int
    today_sessions: int
    week_minutes: int
    week_sessions: int
    total_minutes: int
    total_sessions: int
