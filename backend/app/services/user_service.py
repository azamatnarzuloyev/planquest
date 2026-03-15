import secrets
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.models.user_progress import UserProgress
from app.models.user_settings import UserSettings
from app.schemas.user import UserCreate, UserUpdate, UserSettingsUpdate


def _generate_referral_code() -> str:
    """Generate a unique 8-character referral code."""
    return secrets.token_urlsafe(6)[:8]


async def get_user_by_telegram_id(db: AsyncSession, telegram_id: int) -> User | None:
    """Find user by Telegram ID."""
    result = await db.execute(select(User).where(User.telegram_id == telegram_id))
    return result.scalar_one_or_none()


async def get_user_by_id(db: AsyncSession, user_id: UUID) -> User | None:
    """Find user by UUID."""
    result = await db.execute(select(User).where(User.id == user_id))
    return result.scalar_one_or_none()


async def create_user(db: AsyncSession, data: UserCreate) -> User:
    """Create a new user with default settings."""
    user = User(
        telegram_id=data.telegram_id,
        first_name=data.first_name,
        last_name=data.last_name,
        username=data.username,
        referral_code=_generate_referral_code(),
    )
    db.add(user)
    await db.flush()

    # Create default settings
    user_settings = UserSettings(user_id=user.id)
    db.add(user_settings)

    # Create default progress
    user_progress = UserProgress(user_id=user.id)
    db.add(user_progress)

    await db.commit()
    await db.refresh(user)
    return user


async def get_or_create_user(
    db: AsyncSession,
    telegram_id: int,
    first_name: str,
    last_name: str | None = None,
    username: str | None = None,
) -> tuple[User, bool]:
    """
    Find or create user by telegram_id.
    Returns (user, is_new).
    If user exists, updates first_name/last_name/username.
    """
    user = await get_user_by_telegram_id(db, telegram_id)

    if user is not None:
        # Update profile fields (may have changed in Telegram)
        changed = False
        if user.first_name != first_name:
            user.first_name = first_name
            changed = True
        if user.last_name != last_name:
            user.last_name = last_name
            changed = True
        if username and user.username != username:
            user.username = username
            changed = True
        if changed:
            await db.commit()
            await db.refresh(user)
        return user, False

    # Create new user
    user = await create_user(
        db,
        UserCreate(
            telegram_id=telegram_id,
            first_name=first_name,
            last_name=last_name,
            username=username,
        ),
    )
    return user, True


async def update_user(db: AsyncSession, user: User, data: UserUpdate) -> User:
    """Update user profile fields."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(user, field, value)
    await db.commit()
    await db.refresh(user)
    return user


async def update_user_settings(
    db: AsyncSession, user: User, data: UserSettingsUpdate
) -> UserSettings:
    """Update user settings."""
    settings = user.settings
    if settings is None:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        await db.flush()

    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(settings, field, value)
    await db.commit()
    await db.refresh(settings)
    return settings
