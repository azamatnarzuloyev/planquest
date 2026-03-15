import uuid
from datetime import datetime

from sqlalchemy import ForeignKey, String, UniqueConstraint
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column

from app.models.base import Base, TimestampMixin, UUIDMixin


class Referral(Base, UUIDMixin, TimestampMixin):
    """Referral tracking — who invited whom."""

    __tablename__ = "referrals"
    __table_args__ = (
        UniqueConstraint("referred_user_id", name="uq_referred_user"),
    )

    referrer_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, index=True
    )
    referred_user_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=False, unique=True
    )
    referral_code: Mapped[str] = mapped_column(String(10), nullable=False)

    # Status: pending (onboarding not done), activated (onboarding done), d7_rewarded
    status: Mapped[str] = mapped_column(String(20), nullable=False, default="pending")

    activated_at: Mapped[datetime | None] = mapped_column(nullable=True)
    d7_rewarded_at: Mapped[datetime | None] = mapped_column(nullable=True)
