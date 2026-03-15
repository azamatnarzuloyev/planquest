from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.user import (
    UserResponse,
    UserSettingsResponse,
    UserSettingsUpdate,
    UserUpdate,
)
from app.schemas.xp import UserProgressResponse
from app.services.stats_service import get_total_stats, get_weekly_completion
from app.services.user_service import update_user, update_user_settings
from app.services.xp_service import get_or_create_progress, get_xp_for_next_level, required_xp_for_level

router = APIRouter(prefix="/api/users", tags=["users"])


@router.get("/me", response_model=UserResponse)
async def get_me(user: User = Depends(get_current_user)) -> UserResponse:
    """Get current authenticated user."""
    return UserResponse.model_validate(user)


@router.patch("/me", response_model=UserResponse)
async def update_me(
    data: UserUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserResponse:
    """Update current user profile."""
    updated = await update_user(db, user, data)
    return UserResponse.model_validate(updated)


@router.get("/me/progress", response_model=UserProgressResponse)
async def get_my_progress(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserProgressResponse:
    """Get current user progress (level, XP, coins)."""
    progress = await get_or_create_progress(db, user.id)
    await db.commit()

    xp_current_level = required_xp_for_level(progress.current_level)
    xp_next_level = get_xp_for_next_level(progress.current_level)
    xp_in_level = progress.total_xp - xp_current_level
    xp_needed = xp_next_level - xp_current_level

    return UserProgressResponse(
        current_level=progress.current_level,
        total_xp=progress.total_xp,
        xp_for_next_level=xp_next_level,
        xp_progress_in_level=xp_in_level,
        progress_percent=round((xp_in_level / xp_needed) * 100, 1) if xp_needed > 0 else 100.0,
        coins_balance=progress.coins_balance,
    )


@router.get("/me/weekly")
async def get_my_weekly(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[dict]:
    """Get weekly completion data for chart."""
    return await get_weekly_completion(db, user.id)


@router.get("/me/stats")
async def get_my_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get all-time stats."""
    return await get_total_stats(db, user.id)


@router.get("/me/settings", response_model=UserSettingsResponse)
async def get_my_settings(
    user: User = Depends(get_current_user),
) -> UserSettingsResponse:
    """Get current user settings."""
    if user.settings is None:
        # Create default settings if missing
        from app.models.user_settings import UserSettings
        from app.core.database import async_session

        async with async_session() as db:
            settings = UserSettings(user_id=user.id)
            db.add(settings)
            await db.commit()
            await db.refresh(settings)
            return UserSettingsResponse.model_validate(settings)

    return UserSettingsResponse.model_validate(user.settings)


@router.patch("/me/settings", response_model=UserSettingsResponse)
async def update_my_settings(
    data: UserSettingsUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> UserSettingsResponse:
    """Update current user settings."""
    settings = await update_user_settings(db, user, data)
    return UserSettingsResponse.model_validate(settings)
