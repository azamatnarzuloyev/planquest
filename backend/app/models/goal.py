import uuid
from datetime import date

from sqlalchemy import Date, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Goal(Base, UUIDMixin, TimestampMixin):
    """User goals with hierarchy: yearly → monthly → weekly."""

    __tablename__ = "goals"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Hierarchy — parent_goal_id for nesting
    parent_goal_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("goals.id", ondelete="SET NULL"), nullable=True
    )

    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False, default="")

    # Category: work, study, health, personal, project, finance
    category: Mapped[str] = mapped_column(String(30), nullable=False, default="personal")

    # Level: yearly, monthly, weekly
    level: Mapped[str] = mapped_column(String(10), nullable=False, default="monthly")

    target_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    # Progress 0-100
    progress_percent: Mapped[float] = mapped_column(Float, nullable=False, default=0.0)

    # Status: active, completed, archived
    status: Mapped[str] = mapped_column(String(15), nullable=False, default="active", index=True)

    # Linked tasks count (cached, updated on task changes)
    linked_tasks_total: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    linked_tasks_done: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
