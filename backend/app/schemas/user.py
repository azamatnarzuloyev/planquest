from datetime import datetime, time
from uuid import UUID

from pydantic import BaseModel, Field


# === User Schemas ===


class UserCreate(BaseModel):
    """Internal schema — bot yoki auth system yangi user yaratganda."""

    telegram_id: int
    first_name: str = Field(max_length=255)
    last_name: str | None = Field(default=None, max_length=255)
    username: str | None = Field(default=None, max_length=255)


class UserUpdate(BaseModel):
    """User o'z profilini yangilash."""

    segment: str | None = Field(default=None, max_length=50)
    timezone: str | None = Field(default=None, max_length=50)
    language: str | None = Field(default=None, max_length=10)
    first_name: str | None = Field(default=None, max_length=255)
    last_name: str | None = Field(default=None, max_length=255)


class UserResponse(BaseModel):
    id: UUID
    telegram_id: int
    first_name: str
    last_name: str | None
    username: str | None
    segment: str | None
    timezone: str
    language: str
    is_premium: bool
    is_active: bool
    onboarding_step: int
    referral_code: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


# === UserSettings Schemas ===


class UserSettingsUpdate(BaseModel):
    """Settings yangilash."""

    morning_reminder_time: time | None = None
    evening_reminder_time: time | None = None
    quiet_hours_start: time | None = None
    quiet_hours_end: time | None = None
    theme: str | None = Field(default=None, max_length=20)


class UserSettingsResponse(BaseModel):
    morning_reminder_time: time
    evening_reminder_time: time
    quiet_hours_start: time
    quiet_hours_end: time
    theme: str
    daily_message_count: int
    max_daily_messages: int

    model_config = {"from_attributes": True}


# === Combined Response ===


class UserWithSettingsResponse(BaseModel):
    user: UserResponse
    settings: UserSettingsResponse | None

    model_config = {"from_attributes": True}
