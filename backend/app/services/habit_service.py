from datetime import date, datetime, timezone
from uuid import UUID

from sqlalchemy import select, func, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import Habit, HabitLog
from app.schemas.habit import HabitCreate, HabitUpdate, HabitLogCreate

HABIT_TYPE_XP = {
    "yes_no": 5,
    "count": 8,
    "duration": 10,
    "avoid": 7,
}


# === Habit CRUD ===


async def create_habit(db: AsyncSession, user_id: UUID, data: HabitCreate) -> Habit:
    habit = Habit(
        user_id=user_id,
        title=data.title,
        type=data.type.value,
        target_value=data.target_value,
        frequency=data.frequency.value,
        frequency_days=data.frequency_days,
        reminder_time=data.reminder_time,
        icon=data.icon,
        color=data.color,
    )
    db.add(habit)
    await db.commit()
    await db.refresh(habit)
    return habit


async def get_habits(
    db: AsyncSession, user_id: UUID, include_archived: bool = False, filter_today: bool = False
) -> list[Habit]:
    query = select(Habit).where(Habit.user_id == user_id)
    if not include_archived:
        query = query.where(Habit.status != "archived")
    query = query.order_by(Habit.created_at.asc())
    result = await db.execute(query)
    habits = list(result.scalars().all())

    if filter_today:
        habits = [h for h in habits if _is_habit_active_today(h)]

    return habits


def _is_habit_active_today(habit: Habit) -> bool:
    """Check if habit should be shown today based on frequency."""
    today_weekday = date.today().weekday()  # 0=Monday, 6=Sunday

    if habit.frequency == "daily":
        return True
    elif habit.frequency == "weekdays":
        return today_weekday < 5  # Mon-Fri
    elif habit.frequency == "3_per_week":
        # Show Mon, Wed, Fri by default
        return today_weekday in (0, 2, 4)
    elif habit.frequency == "custom":
        if habit.frequency_days:
            return today_weekday in habit.frequency_days
        return True
    return True


async def get_habit_by_id(db: AsyncSession, habit_id: UUID, user_id: UUID) -> Habit | None:
    result = await db.execute(
        select(Habit).where(Habit.id == habit_id, Habit.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def update_habit(db: AsyncSession, habit: Habit, data: HabitUpdate) -> Habit:
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):
            value = value.value
        setattr(habit, field, value)
    await db.commit()
    await db.refresh(habit)
    return habit


async def archive_habit(db: AsyncSession, habit: Habit) -> Habit:
    habit.status = "archived"
    await db.commit()
    await db.refresh(habit)
    return habit


# === Habit Logging ===


async def get_habit_log(
    db: AsyncSession, habit_id: UUID, user_id: UUID, log_date: date
) -> HabitLog | None:
    result = await db.execute(
        select(HabitLog).where(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == user_id,
            HabitLog.date == log_date,
        )
    )
    return result.scalar_one_or_none()


async def log_habit(
    db: AsyncSession, habit: Habit, data: HabitLogCreate
) -> tuple[HabitLog, bool]:
    """
    Log a habit for a given date.
    Returns (log, is_new). If log exists for that date, updates it.
    """
    log_date = data.log_date or date.today()
    completed = data.value >= habit.target_value

    existing = await get_habit_log(db, habit.id, habit.user_id, log_date)
    if existing is not None:
        existing.value = data.value
        existing.completed = completed
        existing.logged_at = datetime.now(timezone.utc).replace(tzinfo=None)
        await db.commit()
        await db.refresh(existing)
        return existing, False

    log = HabitLog(
        habit_id=habit.id,
        user_id=habit.user_id,
        date=log_date,
        value=data.value,
        completed=completed,
        logged_at=datetime.now(timezone.utc).replace(tzinfo=None),
        source=data.source,
    )
    db.add(log)
    await db.commit()
    await db.refresh(log)
    return log, True


async def get_habit_logs(
    db: AsyncSession, habit_id: UUID, user_id: UUID,
    from_date: date | None = None, to_date: date | None = None,
) -> list[HabitLog]:
    query = select(HabitLog).where(
        HabitLog.habit_id == habit_id,
        HabitLog.user_id == user_id,
    )
    if from_date:
        query = query.where(HabitLog.date >= from_date)
    if to_date:
        query = query.where(HabitLog.date <= to_date)
    query = query.order_by(HabitLog.date.desc())
    result = await db.execute(query)
    return list(result.scalars().all())


# === Streak Calculation ===


async def calculate_habit_streak(db: AsyncSession, habit_id: UUID, user_id: UUID) -> int:
    """Calculate current streak for a habit by counting consecutive completed days backwards."""
    logs = await db.execute(
        select(HabitLog.date).where(
            HabitLog.habit_id == habit_id,
            HabitLog.user_id == user_id,
            HabitLog.completed == True,
        ).order_by(HabitLog.date.desc())
    )
    completed_dates = [row[0] for row in logs.all()]

    if not completed_dates:
        return 0

    streak = 0
    expected = date.today()

    for d in completed_dates:
        if d == expected:
            streak += 1
            expected = date.fromordinal(expected.toordinal() - 1)
        elif d < expected:
            break

    return streak


def get_habit_xp(habit_type: str) -> int:
    """Get base XP for a habit type."""
    return HABIT_TYPE_XP.get(habit_type, 5)
