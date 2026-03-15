"""Mission generation and progress tracking service."""

import random
from datetime import date, datetime, timedelta
from uuid import UUID

from sqlalchemy import and_, select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.mission import Mission
from app.services.xp_service import award_xp


# === Mission templates ===

DAILY_EASY = [
    {"title": "Bitta task bajar", "action": "tasks_completed", "target": 1, "xp": 15, "coins": 5},
    {"title": "Bitta habit qayd qil", "action": "habits_logged", "target": 1, "xp": 15, "coins": 5},
    {"title": "10 daqiqa fokus", "action": "focus_minutes", "target": 10, "xp": 15, "coins": 5},
]

DAILY_MEDIUM = [
    {"title": "3 ta task bajar", "action": "tasks_completed", "target": 3, "xp": 30, "coins": 10},
    {"title": "25 daqiqa fokus sessiya", "action": "focus_minutes", "target": 25, "xp": 30, "coins": 10},
    {"title": "2 ta habit qayd qil", "action": "habits_logged", "target": 2, "xp": 30, "coins": 10},
    {"title": "1 ta fokus sessiya tugat", "action": "focus_sessions", "target": 1, "xp": 25, "coins": 8},
]

DAILY_STRETCH = [
    {"title": "5 ta task bajar", "action": "tasks_completed", "target": 5, "xp": 50, "coins": 20},
    {"title": "50 daqiqa fokus", "action": "focus_minutes", "target": 50, "xp": 50, "coins": 20},
    {"title": "Barcha habitlarni bajar", "action": "all_habits_done", "target": 1, "xp": 60, "coins": 25},
    {"title": "3 ta fokus sessiya", "action": "focus_sessions", "target": 3, "xp": 50, "coins": 20},
]

WEEKLY_MISSIONS = [
    {"title": "15 ta task bajar", "action": "tasks_completed", "target": 15, "xp": 100, "coins": 40},
    {"title": "5 kun streak saqla", "action": "streak_days", "target": 5, "xp": 120, "coins": 50},
    {"title": "200 daqiqa fokus", "action": "focus_minutes", "target": 200, "xp": 100, "coins": 40},
    {"title": "7 ta fokus sessiya", "action": "focus_sessions", "target": 7, "xp": 80, "coins": 30},
    {"title": "10 ta habit qayd qil", "action": "habits_logged", "target": 10, "xp": 90, "coins": 35},
    {"title": "20 ta task bajar", "action": "tasks_completed", "target": 20, "xp": 150, "coins": 60},
    {"title": "Har kuni kamida 1 habit", "action": "habit_streak_days", "target": 5, "xp": 100, "coins": 40},
]


async def get_missions(
    db: AsyncSession,
    user_id: UUID,
    mission_type: str = "daily",
    target_date: date | None = None,
) -> list[Mission]:
    """Get missions for user by type and date."""
    if target_date is None:
        target_date = date.today()

    # For weekly — find the Monday of the week
    if mission_type == "weekly":
        target_date = target_date - timedelta(days=target_date.weekday())

    result = await db.execute(
        select(Mission)
        .where(
            and_(
                Mission.user_id == user_id,
                Mission.type == mission_type,
                Mission.assigned_date == target_date,
            )
        )
        .order_by(Mission.created_at)
    )
    return list(result.scalars().all())


async def generate_daily_missions(db: AsyncSession, user_id: UUID, target_date: date | None = None) -> list[Mission]:
    """Generate 3 daily missions: easy, medium, stretch."""
    if target_date is None:
        target_date = date.today()

    # Check if already generated
    existing = await get_missions(db, user_id, "daily", target_date)
    if existing:
        return existing

    missions = []
    templates = [
        (random.choice(DAILY_EASY), "easy"),
        (random.choice(DAILY_MEDIUM), "medium"),
        (random.choice(DAILY_STRETCH), "stretch"),
    ]

    for tmpl, difficulty in templates:
        m = Mission(
            user_id=user_id,
            type="daily",
            difficulty=difficulty,
            title=tmpl["title"],
            description=f"{tmpl['target']} {tmpl['action'].replace('_', ' ')}",
            action=tmpl["action"],
            target_value=tmpl["target"],
            current_value=0,
            reward_xp=tmpl["xp"],
            reward_coins=tmpl["coins"],
            status="active",
            assigned_date=target_date,
        )
        db.add(m)
        missions.append(m)

    await db.flush()
    return missions


async def generate_weekly_missions(db: AsyncSession, user_id: UUID, target_date: date | None = None) -> list[Mission]:
    """Generate 4 weekly missions on Monday."""
    if target_date is None:
        target_date = date.today()

    # Find Monday of this week
    monday = target_date - timedelta(days=target_date.weekday())

    existing = await get_missions(db, user_id, "weekly", monday)
    if existing:
        return existing

    selected = random.sample(WEEKLY_MISSIONS, min(4, len(WEEKLY_MISSIONS)))
    missions = []

    for tmpl in selected:
        m = Mission(
            user_id=user_id,
            type="weekly",
            difficulty="weekly",
            title=tmpl["title"],
            description=f"{tmpl['target']} {tmpl['action'].replace('_', ' ')}",
            action=tmpl["action"],
            target_value=tmpl["target"],
            current_value=0,
            reward_xp=tmpl["xp"],
            reward_coins=tmpl["coins"],
            status="active",
            assigned_date=monday,
        )
        db.add(m)
        missions.append(m)

    await db.flush()
    return missions


async def update_mission_progress(
    db: AsyncSession,
    user_id: UUID,
    action: str,
    increment: int = 1,
) -> list[Mission]:
    """Update progress for all active missions matching the action.
    Returns list of missions that were just completed."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())

    # Find active missions with matching action
    result = await db.execute(
        select(Mission).where(
            and_(
                Mission.user_id == user_id,
                Mission.action == action,
                Mission.status == "active",
                Mission.assigned_date.in_([today, monday]),
            )
        )
    )
    missions = list(result.scalars().all())
    completed = []

    for m in missions:
        m.current_value = min(m.current_value + increment, m.target_value)

        if m.current_value >= m.target_value:
            m.status = "completed"
            m.completed_at = datetime.utcnow()

            # Award XP and coins
            await award_xp(db, user_id, "mission", m.id, m.reward_xp, coins=m.reward_coins)

            # Check mission achievements
            from app.services.achievement_service import check_achievements
            await check_achievements(db, user_id, "missions_completed", 1)

            completed.append(m)

    # Check if all daily/weekly missions are complete → generate chest
    if completed:
        await _check_all_missions_complete(db, user_id, today, monday)

    if missions:
        await db.flush()

    return completed


async def _check_all_missions_complete(db: AsyncSession, user_id: UUID, today: date, monday: date) -> None:
    """If all daily or weekly missions are complete, create a chest."""
    from app.services.chest_service import create_chest

    # Check daily
    daily_result = await db.execute(
        select(Mission).where(
            and_(Mission.user_id == user_id, Mission.type == "daily", Mission.assigned_date == today)
        )
    )
    daily = list(daily_result.scalars().all())
    if daily and all(m.status == "completed" for m in daily):
        # Check if chest already created today
        from app.models.chest import Chest
        existing = await db.execute(
            select(Chest).where(
                and_(Chest.user_id == user_id, Chest.type == "daily_mission",
                     Chest.source == str(today))
            )
        )
        if existing.scalar_one_or_none() is None:
            await create_chest(db, user_id, "daily_mission", str(today))

    # Check weekly
    weekly_result = await db.execute(
        select(Mission).where(
            and_(Mission.user_id == user_id, Mission.type == "weekly", Mission.assigned_date == monday)
        )
    )
    weekly = list(weekly_result.scalars().all())
    if weekly and all(m.status == "completed" for m in weekly):
        from app.models.chest import Chest
        existing = await db.execute(
            select(Chest).where(
                and_(Chest.user_id == user_id, Chest.type == "weekly_mission",
                     Chest.source == str(monday))
            )
        )
        if existing.scalar_one_or_none() is None:
            await create_chest(db, user_id, "weekly_mission", str(monday))


async def expire_old_missions(db: AsyncSession) -> int:
    """Expire daily missions from yesterday and weekly from last week."""
    today = date.today()
    last_monday = today - timedelta(days=today.weekday() + 7)

    result = await db.execute(
        update(Mission)
        .where(
            and_(
                Mission.status == "active",
                # Daily expired if date < today, weekly if date < last monday
                (
                    ((Mission.type == "daily") & (Mission.assigned_date < today))
                    | ((Mission.type == "weekly") & (Mission.assigned_date < last_monday))
                ),
            )
        )
        .values(status="expired")
    )
    await db.flush()
    return result.rowcount  # type: ignore[return-value]
