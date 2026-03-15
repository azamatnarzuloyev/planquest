import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, UUIDMixin


class FocusSession(Base, UUIDMixin):
    __tablename__ = "focus_sessions"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    task_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("tasks.id", ondelete="SET NULL"), nullable=True
    )

    planned_duration: Mapped[int] = mapped_column(Integer, nullable=False)  # minutes
    actual_duration: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    mode: Mapped[str] = mapped_column(
        String(20), nullable=False
    )  # pomodoro_25, deep_50, ultra_90, custom

    status: Mapped[str] = mapped_column(
        String(20), server_default="active", nullable=False
    )  # active, completed, abandoned

    started_at: Mapped[datetime] = mapped_column(DateTime, nullable=False)
    ended_at: Mapped[datetime | None] = mapped_column(DateTime, nullable=True)
    xp_awarded: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    def __repr__(self) -> str:
        return f"<FocusSession {self.mode} {self.status} {self.planned_duration}min>"
