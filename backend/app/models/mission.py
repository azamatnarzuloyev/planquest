import uuid
from datetime import date, datetime

from sqlalchemy import Date, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Mission(Base, UUIDMixin, TimestampMixin):
    """Daily and weekly missions for gamification."""

    __tablename__ = "missions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Type: daily / weekly
    type: Mapped[str] = mapped_column(String(10), nullable=False, index=True)

    # Difficulty: easy / medium / stretch (daily), or weekly
    difficulty: Mapped[str] = mapped_column(String(20), nullable=False, default="easy")

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # What action to track: tasks_completed, habits_logged, focus_minutes, focus_sessions, streak_days
    action: Mapped[str] = mapped_column(String(50), nullable=False)

    target_value: Mapped[int] = mapped_column(Integer, nullable=False, default=1)
    current_value: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    reward_xp: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    reward_coins: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    # Status: active / completed / expired
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="active", index=True)

    # For daily — specific date, for weekly — Monday of that week
    assigned_date: Mapped[date] = mapped_column(Date, nullable=False, index=True)

    completed_at: Mapped[datetime | None] = mapped_column(nullable=True)
