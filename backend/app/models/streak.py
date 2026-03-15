import uuid
from datetime import date

from sqlalchemy import Date, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Streak(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "streaks"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True
    )
    type: Mapped[str] = mapped_column(
        String(50), nullable=False
    )  # "activity", "focus", "planning", "habit_{uuid}"

    current_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    best_count: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    last_active_date: Mapped[date | None] = mapped_column(Date, nullable=True)

    __table_args__ = (
        UniqueConstraint("user_id", "type", name="uq_streaks_user_type"),
    )

    def __repr__(self) -> str:
        return f"<Streak {self.type} count={self.current_count}>"
