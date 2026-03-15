"""Achievement catalog, seeding, and event-driven progress tracking."""

import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.achievement import Achievement, UserAchievement
from app.services.xp_service import award_xp

logger = logging.getLogger(__name__)

# === Achievement Catalog ===
# requirement_type maps to event names: tasks_completed, habits_logged, focus_minutes, etc.

ACHIEVEMENT_CATALOG = [
    # --- Tasks ---
    {"key": "first_task", "name": "Birinchi qadam", "desc": "Birinchi taskni bajaring", "cat": "tasks", "icon": "✅", "req": "tasks_completed", "val": 1, "xp": 20, "coins": 10, "order": 1},
    {"key": "task_10", "name": "Ishchan", "desc": "10 ta task bajaring", "cat": "tasks", "icon": "📋", "req": "tasks_completed", "val": 10, "xp": 50, "coins": 20, "order": 2},
    {"key": "task_50", "name": "Productive Pro", "desc": "50 ta task bajaring", "cat": "tasks", "icon": "🏅", "req": "tasks_completed", "val": 50, "xp": 150, "coins": 60, "order": 3},
    {"key": "task_100", "name": "Task Centurion", "desc": "100 ta task bajaring", "cat": "tasks", "icon": "💯", "req": "tasks_completed", "val": 100, "xp": 300, "coins": 120, "order": 4},
    {"key": "task_500", "name": "Task Machine", "desc": "500 ta task bajaring", "cat": "tasks", "icon": "⚡", "req": "tasks_completed", "val": 500, "xp": 500, "coins": 200, "order": 5},

    # --- Habits ---
    {"key": "first_habit", "name": "Odat boshlandi", "desc": "Birinchi habitni loglang", "cat": "habits", "icon": "🔄", "req": "habits_logged", "val": 1, "xp": 20, "coins": 10, "order": 10},
    {"key": "habit_30", "name": "Habit Builder", "desc": "30 marta habit loglang", "cat": "habits", "icon": "🧱", "req": "habits_logged", "val": 30, "xp": 100, "coins": 40, "order": 11},
    {"key": "habit_100", "name": "Odat ustasi", "desc": "100 marta habit loglang", "cat": "habits", "icon": "🏆", "req": "habits_logged", "val": 100, "xp": 250, "coins": 100, "order": 12},
    {"key": "habit_365", "name": "Yillik odat", "desc": "365 marta habit loglang", "cat": "habits", "icon": "📅", "req": "habits_logged", "val": 365, "xp": 500, "coins": 200, "order": 13},

    # --- Focus ---
    {"key": "first_focus", "name": "Diqqat!", "desc": "Birinchi fokus sessiyani tugatang", "cat": "focus", "icon": "🎯", "req": "focus_sessions", "val": 1, "xp": 20, "coins": 10, "order": 20},
    {"key": "focus_10h", "name": "Deep Worker", "desc": "Jami 10 soat fokus qiling", "cat": "focus", "icon": "🧠", "req": "focus_minutes", "val": 600, "xp": 200, "coins": 80, "order": 21},
    {"key": "focus_50h", "name": "Focus Master", "desc": "Jami 50 soat fokus qiling", "cat": "focus", "icon": "🔥", "req": "focus_minutes", "val": 3000, "xp": 500, "coins": 200, "order": 22},
    {"key": "focus_100h", "name": "100 Soat Klubi", "desc": "Jami 100 soat fokus qiling", "cat": "focus", "icon": "💎", "req": "focus_minutes", "val": 6000, "xp": 1000, "coins": 400, "order": 23},
    {"key": "focus_20_sessions", "name": "Focused Mind", "desc": "20 ta fokus sessiya tugatang", "cat": "focus", "icon": "🧘", "req": "focus_sessions", "val": 20, "xp": 100, "coins": 40, "order": 24},

    # --- Streaks ---
    {"key": "streak_3", "name": "3 kunlik streak", "desc": "3 kun ketma-ket faol bo'ling", "cat": "streaks", "icon": "🔥", "req": "streak_days", "val": 3, "xp": 30, "coins": 15, "order": 30},
    {"key": "streak_7", "name": "7-Day Warrior", "desc": "7 kun ketma-ket faol bo'ling", "cat": "streaks", "icon": "⚔️", "req": "streak_days", "val": 7, "xp": 75, "coins": 30, "order": 31},
    {"key": "streak_14", "name": "2 haftalik streak", "desc": "14 kun ketma-ket faol bo'ling", "cat": "streaks", "icon": "🛡️", "req": "streak_days", "val": 14, "xp": 150, "coins": 60, "order": 32},
    {"key": "streak_30", "name": "Monthly Champion", "desc": "30 kun ketma-ket faol bo'ling", "cat": "streaks", "icon": "👑", "req": "streak_days", "val": 30, "xp": 300, "coins": 120, "order": 33},
    {"key": "streak_100", "name": "100 kun legenda", "desc": "100 kun ketma-ket faol bo'ling", "cat": "streaks", "icon": "🌟", "req": "streak_days", "val": 100, "xp": 1000, "coins": 500, "order": 34},

    # --- Missions ---
    {"key": "mission_first", "name": "Missiya qabul qilindi", "desc": "Birinchi missiyani bajaring", "cat": "missions", "icon": "🎯", "req": "missions_completed", "val": 1, "xp": 25, "coins": 10, "order": 40},
    {"key": "mission_10", "name": "Mission Runner", "desc": "10 ta missiya bajaring", "cat": "missions", "icon": "🏃", "req": "missions_completed", "val": 10, "xp": 100, "coins": 40, "order": 41},
    {"key": "mission_50", "name": "Mission Expert", "desc": "50 ta missiya bajaring", "cat": "missions", "icon": "🎖️", "req": "missions_completed", "val": 50, "xp": 300, "coins": 120, "order": 42},

    # --- Levels ---
    {"key": "level_5", "name": "Rising Star", "desc": "Level 5 ga chiqing", "cat": "levels", "icon": "⭐", "req": "level_reached", "val": 5, "xp": 50, "coins": 25, "order": 50},
    {"key": "level_10", "name": "Veteran", "desc": "Level 10 ga chiqing", "cat": "levels", "icon": "🌟", "req": "level_reached", "val": 10, "xp": 100, "coins": 50, "order": 51},
    {"key": "level_25", "name": "Legend", "desc": "Level 25 ga chiqing", "cat": "levels", "icon": "💫", "req": "level_reached", "val": 25, "xp": 300, "coins": 150, "order": 52},
]


async def seed_achievements(db: AsyncSession) -> int:
    """Seed achievement catalog. Returns count of new achievements added."""
    existing = await db.execute(select(Achievement.key))
    existing_keys = set(existing.scalars().all())

    added = 0
    for a in ACHIEVEMENT_CATALOG:
        if a["key"] not in existing_keys:
            db.add(Achievement(
                key=a["key"], name=a["name"], description=a["desc"],
                category=a["cat"], icon=a["icon"],
                requirement_type=a["req"], requirement_value=a["val"],
                reward_xp=a["xp"], reward_coins=a["coins"],
                sort_order=a["order"],
            ))
            added += 1

    if added:
        await db.flush()
    return added


async def get_all_achievements(db: AsyncSession) -> list[Achievement]:
    """Get all achievements ordered by sort_order."""
    result = await db.execute(select(Achievement).order_by(Achievement.sort_order))
    return list(result.scalars().all())


async def get_user_achievements(db: AsyncSession, user_id: UUID) -> dict[UUID, UserAchievement]:
    """Get all user achievement progress as {achievement_id: UserAchievement}."""
    result = await db.execute(
        select(UserAchievement).where(UserAchievement.user_id == user_id)
    )
    return {ua.achievement_id: ua for ua in result.scalars().all()}


async def _get_or_create_user_achievement(
    db: AsyncSession, user_id: UUID, achievement_id: UUID
) -> UserAchievement:
    """Get or create user achievement record."""
    result = await db.execute(
        select(UserAchievement).where(
            and_(UserAchievement.user_id == user_id, UserAchievement.achievement_id == achievement_id)
        )
    )
    ua = result.scalar_one_or_none()
    if ua is None:
        ua = UserAchievement(user_id=user_id, achievement_id=achievement_id, progress=0)
        db.add(ua)
        await db.flush()
    return ua


async def check_achievements(
    db: AsyncSession,
    user_id: UUID,
    event_type: str,
    increment: int = 1,
) -> list[dict]:
    """
    Check and update achievements matching the event_type.
    Returns list of newly unlocked achievements.
    """
    # Get all achievements with matching requirement_type
    result = await db.execute(
        select(Achievement).where(Achievement.requirement_type == event_type)
    )
    achievements = list(result.scalars().all())
    if not achievements:
        return []

    unlocked = []

    for ach in achievements:
        ua = await _get_or_create_user_achievement(db, user_id, ach.id)

        if ua.unlocked:
            continue

        # For streak_days and level_reached, set absolute value instead of increment
        if event_type in ("streak_days", "level_reached"):
            ua.progress = max(ua.progress, increment)
        else:
            ua.progress += increment

        if ua.progress >= ach.requirement_value:
            ua.unlocked = True
            ua.unlocked_at = datetime.utcnow()

            # Award XP + coins
            await award_xp(db, user_id, "achievement", ach.id, ach.reward_xp, coins=ach.reward_coins)

            unlocked.append({
                "key": ach.key,
                "name": ach.name,
                "icon": ach.icon,
                "xp": ach.reward_xp,
                "coins": ach.reward_coins,
            })
            logger.info(f"Achievement unlocked: {ach.key} for user {user_id}")

    if unlocked or achievements:
        await db.flush()

    return unlocked
