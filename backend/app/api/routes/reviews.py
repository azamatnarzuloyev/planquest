"""Weekly review endpoint."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends, Query
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.focus_session import FocusSession
from app.models.habit import HabitLog
from app.models.task import Task
from app.models.user import User
from app.services.streak_service import get_user_streaks
from app.services.xp_service import get_or_create_progress

router = APIRouter(prefix="/api/reviews", tags=["reviews"])


@router.get("/weekly")
async def weekly_review(
    week: str | None = Query(default=None, description="ISO week e.g. 2026-W12"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get weekly review stats."""
    today = date.today()

    if week:
        # Parse ISO week
        import datetime as dt
        year, w = week.split("-W")
        monday = dt.date.fromisocalendar(int(year), int(w), 1)
    else:
        # Current week (Monday)
        monday = today - timedelta(days=today.weekday())

    sunday = monday + timedelta(days=6)

    # Tasks
    tasks_result = await db.execute(
        select(Task).where(
            and_(Task.user_id == user.id, Task.planned_date >= monday, Task.planned_date <= sunday, Task.status != "archived")
        )
    )
    tasks = list(tasks_result.scalars().all())
    tasks_total = len(tasks)
    tasks_completed = sum(1 for t in tasks if t.status == "completed")
    tasks_pending = sum(1 for t in tasks if t.status == "pending")

    # Habits
    habits_result = await db.execute(
        select(func.count()).where(
            and_(HabitLog.user_id == user.id, HabitLog.date >= monday, HabitLog.date <= sunday, HabitLog.completed == True)
        )
    )
    habits_completed = habits_result.scalar_one()

    habits_total = await db.execute(
        select(func.count()).where(
            and_(HabitLog.user_id == user.id, HabitLog.date >= monday, HabitLog.date <= sunday)
        )
    )
    habits_logged = habits_total.scalar_one()

    # Focus
    focus_result = await db.execute(
        select(
            func.coalesce(func.sum(FocusSession.actual_duration), 0),
            func.count(),
        ).where(
            and_(
                FocusSession.user_id == user.id,
                func.date(FocusSession.started_at) >= monday,
                func.date(FocusSession.started_at) <= sunday,
                FocusSession.status == "completed",
            )
        )
    )
    focus_row = focus_result.one()
    focus_minutes = focus_row[0]
    focus_sessions = focus_row[1]

    # XP earned this week
    from app.models.xp_event import XpEvent
    xp_result = await db.execute(
        select(func.coalesce(func.sum(XpEvent.xp_amount), 0)).where(
            and_(XpEvent.user_id == user.id, func.date(XpEvent.created_at) >= monday, func.date(XpEvent.created_at) <= sunday)
        )
    )
    xp_earned = xp_result.scalar_one()

    # Streak
    streaks = await get_user_streaks(db, user.id)
    activity = next((s for s in streaks if s.type == "activity"), None)

    # Progress
    progress = await get_or_create_progress(db, user.id)

    # Daily breakdown
    daily = []
    for i in range(7):
        d = monday + timedelta(days=i)
        day_tasks = sum(1 for t in tasks if t.status == "completed" and t.completed_at and t.completed_at.date() == d)
        daily.append({
            "date": d.isoformat(),
            "day": ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"][i],
            "tasks": day_tasks,
            "is_today": d == today,
            "is_future": d > today,
        })

    return {
        "week": f"{monday.isocalendar()[0]}-W{monday.isocalendar()[1]:02d}",
        "monday": monday.isoformat(),
        "sunday": sunday.isoformat(),
        "tasks": {
            "total": tasks_total,
            "completed": tasks_completed,
            "pending": tasks_pending,
            "completion_rate": round(tasks_completed / tasks_total * 100, 1) if tasks_total > 0 else 0,
        },
        "habits": {
            "completed": habits_completed,
            "logged": habits_logged,
        },
        "focus": {
            "minutes": focus_minutes,
            "sessions": focus_sessions,
        },
        "xp_earned": xp_earned,
        "level": progress.current_level,
        "streak": activity.current_count if activity else 0,
        "daily": daily,
    }
