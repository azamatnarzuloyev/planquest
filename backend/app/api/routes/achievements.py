from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.achievement import AchievementResponse
from app.services.achievement_service import get_all_achievements, get_user_achievements, seed_achievements

router = APIRouter(prefix="/api/achievements", tags=["achievements"])


@router.get("", response_model=list[AchievementResponse])
async def list_achievements(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[AchievementResponse]:
    """Get all achievements with user progress. Seeds catalog on first call."""
    # Seed if needed
    added = await seed_achievements(db)
    if added:
        await db.commit()

    achievements = await get_all_achievements(db)
    user_progress = await get_user_achievements(db, user.id)

    result = []
    for ach in achievements:
        ua = user_progress.get(ach.id)
        result.append(AchievementResponse(
            id=ach.id,
            key=ach.key,
            name=ach.name,
            description=ach.description,
            category=ach.category,
            icon=ach.icon,
            requirement_type=ach.requirement_type,
            requirement_value=ach.requirement_value,
            reward_xp=ach.reward_xp,
            reward_coins=ach.reward_coins,
            progress=ua.progress if ua else 0,
            unlocked=ua.unlocked if ua else False,
            unlocked_at=ua.unlocked_at if ua else None,
        ))

    return result
