import logging
from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.streak import Streak
from app.models.user_progress import UserProgress

logger = logging.getLogger(__name__)

# Milestone: streak days → coins reward
STREAK_MILESTONES = {
    3: 0,
    7: 25,
    14: 50,
    30: 100,
    60: 200,
    90: 300,
    180: 500,
    365: 1000,
}


async def get_or_create_streak(db: AsyncSession, user_id: UUID, streak_type: str) -> Streak:
    """Find or create a streak record."""
    result = await db.execute(
        select(Streak).where(Streak.user_id == user_id, Streak.type == streak_type)
    )
    streak = result.scalar_one_or_none()
    if streak is None:
        streak = Streak(user_id=user_id, type=streak_type)
        db.add(streak)
        await db.flush()
    return streak


async def update_streak(db: AsyncSession, user_id: UUID, streak_type: str) -> dict:
    """
    Update streak for today. Idempotent — calling multiple times per day has no effect.

    Returns: {current_count, best_count, is_milestone, milestone_coins}
    """
    streak = await get_or_create_streak(db, user_id, streak_type)
    today = date.today()
    yesterday = today - timedelta(days=1)

    # Already updated today — idempotent
    if streak.last_active_date == today:
        is_milestone, milestone_coins = check_milestone(streak.current_count)
        return {
            "current_count": streak.current_count,
            "best_count": streak.best_count,
            "is_milestone": False,  # Don't re-trigger milestone
            "milestone_coins": 0,
        }

    # Consecutive day — increment
    if streak.last_active_date == yesterday:
        streak.current_count += 1
    # Gap of exactly 1 day — check for streak freeze (only for activity streak)
    elif (
        streak_type == "activity"
        and streak.last_active_date is not None
        and streak.current_count > 0
        and (today - streak.last_active_date).days == 2  # missed exactly 1 day
    ):
        from app.services.wallet_service import use_item
        frozen = await use_item(db, user_id, "streak_freeze")
        if frozen:
            # Freeze saved the streak — continue counting
            streak.current_count += 1
            logger.info(f"Streak freeze used for user {user_id}, streak saved at {streak.current_count}")
        else:
            streak.current_count = 1
    # First day or bigger gap — reset to 1
    else:
        streak.current_count = 1

    streak.last_active_date = today

    # Update best
    if streak.current_count > streak.best_count:
        streak.best_count = streak.current_count

    # Check milestone
    is_milestone, milestone_coins = check_milestone(streak.current_count)

    # Award milestone coins + create chest
    if is_milestone and streak_type == "activity":
        from app.services.chest_service import create_chest
        await create_chest(db, user_id, "streak", f"streak_{streak.current_count}")

    if is_milestone and milestone_coins > 0:
        progress_result = await db.execute(
            select(UserProgress).where(UserProgress.user_id == user_id)
        )
        progress = progress_result.scalar_one_or_none()
        if progress:
            progress.coins_balance += milestone_coins

    # Check streak achievements (only for activity streak)
    if streak_type == "activity":
        from app.services.achievement_service import check_achievements
        await check_achievements(db, user_id, "streak_days", streak.current_count)

    await db.flush()

    logger.info(
        f"Streak updated: user={user_id} type={streak_type} "
        f"count={streak.current_count} milestone={is_milestone}"
    )

    return {
        "current_count": streak.current_count,
        "best_count": streak.best_count,
        "is_milestone": is_milestone,
        "milestone_coins": milestone_coins,
    }


def check_milestone(current_count: int) -> tuple[bool, int]:
    """Check if current count hits a milestone. Returns (is_milestone, coins)."""
    if current_count in STREAK_MILESTONES:
        return True, STREAK_MILESTONES[current_count]
    return False, 0


async def get_user_streaks(db: AsyncSession, user_id: UUID) -> list[Streak]:
    """Get all streaks for a user."""
    result = await db.execute(
        select(Streak)
        .where(Streak.user_id == user_id)
        .order_by(Streak.type.asc())
    )
    return list(result.scalars().all())
