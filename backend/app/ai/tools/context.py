"""Build minimal user context for AI agents. Read-only access to domain services."""

from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.schemas.context import HabitContext, TaskContext, UserContext
from app.services.focus_service import get_focus_stats
from app.services.habit_service import get_habit_log, get_habits
from app.services.streak_service import get_user_streaks
from app.services.task_service import get_tasks
from app.services.xp_service import get_or_create_progress


async def build_planner_context(db: AsyncSession, user_id: UUID, user) -> dict:
    """Build context for Planner Agent."""
    today = date.today()
    today_str = today.isoformat()

    # Fetch data in parallel-ish (sequential for now, can optimize later)
    pending = await get_tasks(db, user_id, planned_date=today, status="pending")
    all_today = await get_tasks(db, user_id, planned_date=today)
    overdue = [t for t in await get_tasks(db, user_id, status="pending") if t.planned_date < today]
    habits_raw = await get_habits(db, user_id, filter_today=True)
    streaks = await get_user_streaks(db, user_id)
    focus = await get_focus_stats(db, user_id)
    progress = await get_or_create_progress(db, user_id)

    # Build habit contexts
    habits = []
    habits_done = 0
    for h in habits_raw[:10]:
        log = await get_habit_log(db, h.id, user_id, today)
        done = bool(log and log.completed)
        if done:
            habits_done += 1
        habits.append(HabitContext(
            id=str(h.id), title=h.title[:50], type=h.type,
            target_value=h.target_value, today_completed=done,
        ))

    activity = next((s for s in streaks if s.type == "activity"), None)

    ctx = UserContext(
        segment=user.segment,
        timezone=user.timezone,
        today_date=today_str,
        day_of_week=today.strftime("%A"),
        pending_tasks=[TaskContext(
            id=str(t.id), title=t.title[:50], priority=t.priority,
            difficulty=t.difficulty, estimated_minutes=t.estimated_minutes,
            planned_date=t.planned_date.isoformat(), category=t.category,
        ) for t in pending[:20]],
        overdue_tasks=[TaskContext(
            id=str(t.id), title=t.title[:50], priority=t.priority,
            difficulty=t.difficulty, estimated_minutes=t.estimated_minutes,
            planned_date=t.planned_date.isoformat(), category=t.category,
        ) for t in overdue[:10]],
        completed_today=sum(1 for t in all_today if t.status == "completed"),
        habits=habits,
        habits_done_today=habits_done,
        streak_current=activity.current_count if activity else 0,
        streak_best=activity.best_count if activity else 0,
        focus_today_minutes=focus["today_minutes"],
        current_level=progress.current_level,
        total_xp=progress.total_xp,
    )

    return ctx.model_dump()
