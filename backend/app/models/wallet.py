import uuid

from sqlalchemy import Integer, String, Text, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class WalletTransaction(Base, UUIDMixin, TimestampMixin):
    """Coin transaction history."""

    __tablename__ = "wallet_transactions"

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Positive = earned, negative = spent
    amount: Mapped[int] = mapped_column(Integer, nullable=False)

    # Type: earn / spend
    type: Mapped[str] = mapped_column(String(10), nullable=False)

    # Source: level_up, mission, achievement, streak_milestone, shop_purchase
    source: Mapped[str] = mapped_column(String(50), nullable=False)

    description: Mapped[str] = mapped_column(Text, nullable=False, default="")


class RewardsInventory(Base, UUIDMixin):
    """User inventory for purchasable items."""

    __tablename__ = "rewards_inventory"
    __table_args__ = (
        UniqueConstraint("user_id", "item_type", name="uq_user_item"),
    )

    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), nullable=False, index=True)

    # Item type: streak_freeze, etc.
    item_type: Mapped[str] = mapped_column(String(50), nullable=False)

    quantity: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
