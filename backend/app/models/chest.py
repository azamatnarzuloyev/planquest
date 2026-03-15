import uuid
from datetime import datetime

from sqlalchemy import Integer, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Chest(Base, UUIDMixin, TimestampMixin):
    """Reward chests earned from missions, streaks, and levels."""

    __tablename__ = "chests"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Type: daily_mission, weekly_mission, streak, level
    type: Mapped[str] = mapped_column(String(20), nullable=False)

    # Rarity: common, rare, epic
    rarity: Mapped[str] = mapped_column(String(10), nullable=False, default="common")

    # Status: unopened, opened
    status: Mapped[str] = mapped_column(String(10), nullable=False, default="unopened", index=True)

    # Source info (e.g., "streak_30", "level_10")
    source: Mapped[str] = mapped_column(String(50), nullable=False, default="")

    # Loot data — JSON string, filled when opened
    loot_data: Mapped[str] = mapped_column(Text, nullable=False, default="{}")

    opened_at: Mapped[datetime | None] = mapped_column(nullable=True)
