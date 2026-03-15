from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.habit import (
    HabitCreate,
    HabitLogCreate,
    HabitLogResponse,
    HabitResponse,
    HabitUpdate,
    HabitWithLogResponse,
)
from app.services.habit_service import (
    archive_habit,
    calculate_habit_streak,
    create_habit,
    get_habit_by_id,
    get_habit_log,
    get_habit_logs,
    get_habit_xp,
    get_habits,
    log_habit,
    update_habit,
)
from app.services.streak_service import update_streak
from app.services.xp_service import award_xp

router = APIRouter(prefix="/api/habits", tags=["habits"])


@router.post("", response_model=HabitResponse, status_code=status.HTTP_201_CREATED)
async def create_habit_endpoint(
    data: HabitCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Create a new habit."""
    habit = await create_habit(db, user.id, data)
    return HabitResponse.model_validate(habit)


@router.get("", response_model=list[HabitWithLogResponse])
async def list_habits(
    all: bool = Query(default=False, description="Show all habits ignoring frequency filter"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HabitWithLogResponse]:
    """List active habits with today's log status and streak. By default filters by today's frequency."""
    habits = await get_habits(db, user.id, filter_today=not all)
    today = date.today()
    result = []
    for habit in habits:
        today_log = await get_habit_log(db, habit.id, user.id, today)
        streak = await calculate_habit_streak(db, habit.id, user.id)
        result.append(HabitWithLogResponse(
            habit=HabitResponse.model_validate(habit),
            today_log=HabitLogResponse.model_validate(today_log) if today_log else None,
            current_streak=streak,
        ))
    return result


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Get a single habit."""
    habit = await get_habit_by_id(db, habit_id, user.id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    return HabitResponse.model_validate(habit)


@router.patch("/{habit_id}", response_model=HabitResponse)
async def update_habit_endpoint(
    habit_id: UUID,
    data: HabitUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HabitResponse:
    """Update a habit."""
    habit = await get_habit_by_id(db, habit_id, user.id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    updated = await update_habit(db, habit, data)
    return HabitResponse.model_validate(updated)


@router.delete("/{habit_id}")
async def delete_habit(
    habit_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Archive a habit."""
    habit = await get_habit_by_id(db, habit_id, user.id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    await archive_habit(db, habit)
    return {"ok": True}


@router.post("/{habit_id}/log", response_model=HabitLogResponse)
async def log_habit_endpoint(
    habit_id: UUID,
    data: HabitLogCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> HabitLogResponse:
    """Log a habit for today (or specified date). Awards XP on first completion."""
    habit = await get_habit_by_id(db, habit_id, user.id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    if habit.status != "active":
        raise HTTPException(status_code=400, detail="Habit is not active")

    log, is_new = await log_habit(db, habit, data)

    xp_awarded = 0
    if is_new and log.completed:
        xp_amount = get_habit_xp(habit.type)
        xp_result = await award_xp(db, user.id, "habit", habit.id, xp_amount)
        xp_awarded = xp_result["xp_awarded"]

        # Update streaks
        await update_streak(db, user.id, "activity")
        await update_streak(db, user.id, f"habit_{habit.id}")

        # Update mission progress
        from app.services.mission_service import update_mission_progress
        await update_mission_progress(db, user.id, "habits_logged", 1)

        # Check achievements
        from app.services.achievement_service import check_achievements
        await check_achievements(db, user.id, "habits_logged", 1)

        await db.commit()

    response = HabitLogResponse.model_validate(log)
    response.xp_awarded = xp_awarded
    return response


@router.get("/{habit_id}/logs", response_model=list[HabitLogResponse])
async def list_habit_logs(
    habit_id: UUID,
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[HabitLogResponse]:
    """Get habit log history."""
    habit = await get_habit_by_id(db, habit_id, user.id)
    if habit is None:
        raise HTTPException(status_code=404, detail="Habit not found")
    logs = await get_habit_logs(db, habit_id, user.id, from_date, to_date)
    return [HabitLogResponse.model_validate(log) for log in logs]
