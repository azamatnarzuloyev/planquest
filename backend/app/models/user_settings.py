import uuid
from datetime import time

from sqlalchemy import ForeignKey, Integer, String, Time
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserSettings(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_settings"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    morning_reminder_time: Mapped[time] = mapped_column(
        Time, server_default="08:00:00", nullable=False
    )
    evening_reminder_time: Mapped[time] = mapped_column(
        Time, server_default="21:00:00", nullable=False
    )
    quiet_hours_start: Mapped[time] = mapped_column(
        Time, server_default="23:00:00", nullable=False
    )
    quiet_hours_end: Mapped[time] = mapped_column(
        Time, server_default="07:00:00", nullable=False
    )

    theme: Mapped[str] = mapped_column(String(20), server_default="system", nullable=False)

    daily_message_count: Mapped[int] = mapped_column(
        Integer, server_default="0", nullable=False
    )
    max_daily_messages: Mapped[int] = mapped_column(
        Integer, server_default="6", nullable=False
    )

    # Relationship
    user: Mapped["User"] = relationship(back_populates="settings")

    def __repr__(self) -> str:
        return f"<UserSettings user_id={self.user_id}>"
