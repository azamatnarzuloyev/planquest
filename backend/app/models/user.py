import uuid

from sqlalchemy import BigInteger, Boolean, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin, UUIDMixin


class User(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "users"

    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, nullable=False, index=True
    )
    first_name: Mapped[str] = mapped_column(String(255), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(255), nullable=True)
    username: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # 4-layer profiling
    segment: Mapped[str | None] = mapped_column(String(50), nullable=True)          # life segment
    main_intent: Mapped[str | None] = mapped_column(String(50), nullable=True)      # what they want help with
    daily_rhythm: Mapped[str | None] = mapped_column(String(20), nullable=True)     # early/normal/late/mixed
    commitment_level: Mapped[str | None] = mapped_column(String(10), nullable=True) # easy/medium/hard

    timezone: Mapped[str] = mapped_column(String(50), server_default="UTC", nullable=False)
    language: Mapped[str] = mapped_column(String(10), server_default="uz", nullable=False)

    is_premium: Mapped[bool] = mapped_column(Boolean, server_default="false", nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, server_default="true", nullable=False)

    onboarding_step: Mapped[int] = mapped_column(Integer, server_default="0", nullable=False)

    referral_code: Mapped[str | None] = mapped_column(
        String(20), unique=True, nullable=True, index=True
    )
    referred_by: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), nullable=True
    )

    # Relationships
    settings: Mapped["UserSettings"] = relationship(
        back_populates="user", uselist=False, cascade="all, delete-orphan", lazy="selectin"
    )

    def __repr__(self) -> str:
        return f"<User {self.telegram_id} ({self.first_name})>"
