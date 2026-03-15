import uuid
from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Task(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "tasks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    planned_date: Mapped[date] = mapped_column(Date, nullable=False)
    due_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    priority: Mapped[str] = mapped_column(
        String(20), server_default="medium", nullable=False
    )
    difficulty: Mapped[str] = mapped_column(
        String(20), server_default="medium", nullable=False
    )
    estimated_minutes: Mapped[int | None] = mapped_column(Integer, nullable=True)
    category: Mapped[str | None] = mapped_column(String(50), nullable=True)

    goal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), nullable=True
    )

    status: Mapped[str] = mapped_column(
        String(20), server_default="pending", nullable=False
    )
    recurrence_rule: Mapped[str | None] = mapped_column(String(100), nullable=True)
    source: Mapped[str] = mapped_column(
        String(20), server_default="mini_app", nullable=False
    )

    completed_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    xp_awarded: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    __table_args__ = (
        Index("ix_tasks_user_id", "user_id"),
        Index("ix_tasks_user_planned_date", "user_id", "planned_date"),
        Index("ix_tasks_status", "status"),
    )

    def __repr__(self) -> str:
        return f"<Task {self.title[:30]} ({self.status})>"
