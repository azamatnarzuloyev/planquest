import math
from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.models.user_progress import UserProgress
from app.models.xp_event import XpEvent

# === XP Constants ===

DIFFICULTY_XP_MAP = {
    "trivial": 5,
    "easy": 10,
    "medium": 20,
    "hard": 35,
    "epic": 50,
}

DAILY_TASK_XP_CAP = 500


# === Level System ===


def required_xp_for_level(level: int) -> int:
    """XP required to reach a given level. Formula: floor(50 × level^1.8)"""
    if level <= 1:
        return 0
    return math.floor(50 * (level ** 1.8))


def get_level_for_xp(total_xp: int) -> int:
    """Determine level based on total XP."""
    level = 1
    while required_xp_for_level(level + 1) <= total_xp:
        level += 1
    return level


def get_xp_for_next_level(current_level: int) -> int:
    """XP needed to reach next level."""
    return required_xp_for_level(current_level + 1)


# === XP Calculation ===


def calculate_task_xp(task: Task) -> int:
    """Calculate XP for completing a task, including multipliers."""
    base_xp = DIFFICULTY_XP_MAP.get(task.difficulty, 20)

    multiplier = 1.0

    # Same-day execution bonus
    today = date.today()
    if task.planned_date == today:
        multiplier *= 1.2

    # Critical priority bonus
    if task.priority == "critical":
        multiplier *= 1.5

    # Goal-linked bonus
    if task.goal_id is not None:
        multiplier *= 1.15

    return math.floor(base_xp * multiplier)


# === Daily XP Tracking ===


async def get_daily_task_xp(db: AsyncSession, user_id: UUID, target_date: date) -> int:
    """Get total task XP earned today."""
    result = await db.execute(
        select(func.coalesce(func.sum(XpEvent.xp_amount), 0)).where(
            XpEvent.user_id == user_id,
            XpEvent.source_type == "task",
            func.date(XpEvent.created_at) == target_date,
        )
    )
    return result.scalar_one()


# === Award XP ===


async def get_or_create_progress(db: AsyncSession, user_id: UUID) -> UserProgress:
    """Get or create user progress record."""
    result = await db.execute(
        select(UserProgress).where(UserProgress.user_id == user_id)
    )
    progress = result.scalar_one_or_none()
    if progress is None:
        progress = UserProgress(user_id=user_id)
        db.add(progress)
        await db.flush()
    return progress


async def award_xp(
    db: AsyncSession,
    user_id: UUID,
    source_type: str,
    source_id: UUID | None,
    xp_amount: int,
    coins: int = 0,
) -> dict:
    """
    Award XP to user. Handles daily cap, level-up, and coin rewards.
    Returns dict with xp_awarded, total_xp, leveled_up, new_level, coins_earned.
    """
    # Check daily cap for tasks
    if source_type == "task":
        today = date.today()
        daily_total = await get_daily_task_xp(db, user_id, today)
        remaining = max(0, DAILY_TASK_XP_CAP - daily_total)
        xp_amount = min(xp_amount, remaining)

    if xp_amount <= 0:
        progress = await get_or_create_progress(db, user_id)
        return {
            "xp_awarded": 0,
            "total_xp": progress.total_xp,
            "leveled_up": False,
            "new_level": progress.current_level,
            "coins_earned": 0,
        }

    # Create XP event
    xp_event = XpEvent(
        user_id=user_id,
        source_type=source_type,
        source_id=source_id,
        xp_amount=xp_amount,
    )
    db.add(xp_event)

    # Update progress
    progress = await get_or_create_progress(db, user_id)
    old_level = progress.current_level
    progress.total_xp += xp_amount

    # Check level-up
    new_level = get_level_for_xp(progress.total_xp)
    leveled_up = new_level > old_level
    coins_earned = 0

    if leveled_up:
        # Award coins for each level gained
        for lvl in range(old_level + 1, new_level + 1):
            coins_earned += lvl * 10

        # Check level achievements
        try:
            from app.services.achievement_service import check_achievements
            await check_achievements(db, user_id, "level_reached", new_level)
        except Exception:
            pass

        # Level chest every 5 levels
        if new_level % 5 == 0:
            try:
                from app.services.chest_service import create_chest
                await create_chest(db, user_id, "level", f"level_{new_level}")
            except Exception:
                pass

    # Add direct coin rewards (e.g. from missions)
    coins_earned += coins
    if coins_earned > 0:
        progress.coins_balance += coins_earned
    if leveled_up:
        progress.current_level = new_level

    await db.flush()

    return {
        "xp_awarded": xp_amount,
        "total_xp": progress.total_xp,
        "leveled_up": leveled_up,
        "new_level": new_level,
        "coins_earned": coins_earned,
    }
