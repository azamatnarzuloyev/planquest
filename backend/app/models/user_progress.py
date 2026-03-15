import uuid

from sqlalchemy import ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class UserProgress(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "user_progress"

    user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )
    total_xp: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)
    current_level: Mapped[int] = mapped_column(Integer, server_default="1", nullable=False)
    coins_balance: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    def __repr__(self) -> str:
        return f"<UserProgress level={self.current_level} xp={self.total_xp}>"
