"""Shareable progress card image endpoints."""

from datetime import date, timedelta

from fastapi import APIRouter, Depends
from fastapi.responses import Response
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.focus_session import FocusSession
from app.models.habit import HabitLog
from app.models.task import Task
from app.models.user import User
from app.services.cards.generator import generate_level_card, generate_streak_card, generate_weekly_card
from app.services.streak_service import get_user_streaks
from app.services.xp_service import get_or_create_progress

router = APIRouter(prefix="/api/cards", tags=["cards"])

LEVEL_TITLES = {
    1: "Yangi boshlovchi", 5: "Beginner Planner", 10: "Rising Star",
    15: "Consistent Worker", 20: "Productivity Pro", 25: "Goal Crusher",
    30: "Deep Worker", 40: "Legendary Planner", 50: "Master",
}


def _get_title(level: int) -> str:
    keys = sorted(LEVEL_TITLES.keys(), reverse=True)
    for k in keys:
        if level >= k:
            return LEVEL_TITLES[k]
    return "Yangi boshlovchi"


@router.get("/streak")
async def streak_card(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate streak progress card as PNG."""
    streaks = await get_user_streaks(db, user.id)
    activity = next((s for s in streaks if s.type == "activity"), None)
    current = activity.current_count if activity else 0
    best = activity.best_count if activity else 0

    png = generate_streak_card(user.first_name, current, best)
    return Response(content=png, media_type="image/png")


@router.get("/level")
async def level_card(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate level progress card as PNG."""
    progress = await get_or_create_progress(db, user.id)
    title = _get_title(progress.current_level)

    png = generate_level_card(user.first_name, progress.current_level, title, progress.total_xp)
    return Response(content=png, media_type="image/png")


@router.get("/weekly")
async def weekly_card(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> Response:
    """Generate weekly win card as PNG."""
    today = date.today()
    monday = today - timedelta(days=today.weekday())
    sunday = monday + timedelta(days=6)

    # Tasks
    tasks_result = await db.execute(
        select(func.count()).where(
            and_(Task.user_id == user.id, Task.planned_date >= monday, Task.planned_date <= sunday, Task.status == "completed")
        )
    )
    tasks_done = tasks_result.scalar_one()

    # Habits
    habits_result = await db.execute(
        select(func.count()).where(
            and_(HabitLog.user_id == user.id, HabitLog.date >= monday, HabitLog.date <= sunday, HabitLog.completed == True)
        )
    )
    habits_done = habits_result.scalar_one()

    # Focus
    focus_result = await db.execute(
        select(func.coalesce(func.sum(FocusSession.actual_duration), 0)).where(
            and_(
                FocusSession.user_id == user.id,
                func.date(FocusSession.started_at) >= monday,
                FocusSession.status == "completed",
            )
        )
    )
    focus_min = focus_result.scalar_one()

    # XP
    from app.models.xp_event import XpEvent
    xp_result = await db.execute(
        select(func.coalesce(func.sum(XpEvent.xp_amount), 0)).where(
            and_(XpEvent.user_id == user.id, func.date(XpEvent.created_at) >= monday)
        )
    )
    xp_earned = xp_result.scalar_one()

    # Streak
    streaks = await get_user_streaks(db, user.id)
    activity = next((s for s in streaks if s.type == "activity"), None)
    streak = activity.current_count if activity else 0

    png = generate_weekly_card(user.first_name, tasks_done, habits_done, focus_min, xp_earned, streak)
    return Response(content=png, media_type="image/png")
