import uuid
from datetime import date, datetime, time

from sqlalchemy import Boolean, Date, DateTime, ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Habit(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "habits"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)

    type: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # yes_no, count, duration, avoid

    target_value: Mapped[int] = mapped_column(
        Integer, server_default="1", nullable=False
    )  # 1 for yes_no/avoid, count target, minutes target

    frequency: Mapped[str] = mapped_column(
        String(20), server_default="daily", nullable=False
    )  # daily, weekdays, weekly, custom

    frequency_days: Mapped[list[int] | None] = mapped_column(
        ARRAY(Integer), nullable=True
    )  # for custom: [1,3,5] = Mon/Wed/Fri (ISO weekday)

    reminder_time: Mapped[time | None] = mapped_column(Time, nullable=True)
    icon: Mapped[str] = mapped_column(String(10), server_default="✅", nullable=False)
    color: Mapped[str] = mapped_column(String(10), server_default="#4CAF50", nullable=False)

    status: Mapped[str] = mapped_column(
        String(20), server_default="active", nullable=False
    )  # active, paused, archived

    def __repr__(self) -> str:
        return f"<Habit {self.title} ({self.type})>"


class HabitLog(Base, UUIDMixin):
    __tablename__ = "habit_logs"

    habit_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("habits.id", ondelete="CASCADE"), nullable=False, index=True
    )
    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    date: Mapped[date] = mapped_column(Date, nullable=False)
    value: Mapped[int] = mapped_column(Integer, nullable=False)  # 1 for yes_no, count, minutes
    completed: Mapped[bool] = mapped_column(Boolean, nullable=False)
    logged_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    source: Mapped[str] = mapped_column(String(20), server_default="mini_app", nullable=False)

    def __repr__(self) -> str:
        return f"<HabitLog {self.date} value={self.value}>"
