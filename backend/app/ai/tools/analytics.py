"""Analytics data for AI agents. Read-only."""

from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.focus_session import FocusSession
from app.models.habit import HabitLog
from app.models.streak import Streak
from app.models.task import Task


async def get_analytics_summary(db: AsyncSession, user_id: UUID, days: int = 14) -> dict:
    """Get aggregated analytics for coaching agent."""
    today = date.today()
    start = today - timedelta(days=days)

    # Task stats
    tasks_result = await db.execute(
        select(Task).where(
            and_(Task.user_id == user_id, Task.planned_date >= start, Task.status != "archived")
        )
    )
    tasks = list(tasks_result.scalars().all())
    total_tasks = len(tasks)
    completed_tasks = sum(1 for t in tasks if t.status == "completed")
    completion_rate = completed_tasks / total_tasks if total_tasks > 0 else 0

    # Habit stats
    habits_result = await db.execute(
        select(func.count()).where(
            and_(HabitLog.user_id == user_id, HabitLog.date >= start, HabitLog.completed == True)
        )
    )
    total_habits_done = habits_result.scalar_one()

    # Focus stats
    focus_result = await db.execute(
        select(func.coalesce(func.sum(FocusSession.actual_duration), 0)).where(
            and_(
                FocusSession.user_id == user_id,
                func.date(FocusSession.started_at) >= start,
                FocusSession.status == "completed",
            )
        )
    )
    total_focus_minutes = focus_result.scalar_one()

    # Streaks
    streaks_result = await db.execute(
        select(Streak).where(and_(Streak.user_id == user_id, Streak.type == "activity"))
    )
    activity_streak = streaks_result.scalar_one_or_none()

    # Weekly breakdown
    weekly = []
    for i in range(min(days, 14)):
        d = today - timedelta(days=i)
        day_tasks = sum(1 for t in tasks if t.status == "completed" and t.completed_at and t.completed_at.date() == d)
        weekly.append({"date": d.isoformat(), "tasks": day_tasks, "habits": 0})

    # Burnout indicators
    if days >= 7:
        recent_7 = [w for w in weekly[:7]]
        older_7 = [w for w in weekly[7:14]] if len(weekly) > 7 else []

        recent_avg = sum(w["tasks"] for w in recent_7) / max(len(recent_7), 1)
        older_avg = sum(w["tasks"] for w in older_7) / max(len(older_7), 1) if older_7 else recent_avg

        declining = recent_avg < older_avg * 0.7 if older_avg > 0 else False
    else:
        declining = False

    return {
        "avg_tasks_per_day": completed_tasks / max(days, 1),
        "task_completion_rate": completion_rate,
        "avg_habits_per_day": total_habits_done / max(days, 1),
        "avg_focus_per_day": total_focus_minutes / max(days, 1),
        "most_productive_hour": "10:00",  # simplified
        "streak_current": activity_streak.current_count if activity_streak else 0,
        "streak_best": activity_streak.best_count if activity_streak else 0,
        "burnout_indicators": {
            "declining_completion": declining,
            "reduced_focus": total_focus_minutes < days * 10,
            "missed_habits_increasing": False,
        },
        "weekly_breakdown": weekly[:7],
    }


async def get_recovery_context(db: AsyncSession, user_id: UUID) -> dict:
    """Get context for recovery agent — missed days, overdue tasks."""
    today = date.today()

    # Find last active date
    streak_result = await db.execute(
        select(Streak).where(and_(Streak.user_id == user_id, Streak.type == "activity"))
    )
    streak = streak_result.scalar_one_or_none()

    if streak and streak.last_active_date:
        missed_days = (today - streak.last_active_date).days
        streak_before = streak.current_count
    else:
        missed_days = 0
        streak_before = 0

    # Overdue tasks
    overdue_result = await db.execute(
        select(Task).where(
            and_(Task.user_id == user_id, Task.planned_date < today, Task.status == "pending")
        ).order_by(Task.priority.desc()).limit(10)
    )
    overdue = [
        {"id": str(t.id), "title": t.title[:50], "priority": t.priority, "planned_date": t.planned_date.isoformat()}
        for t in overdue_result.scalars().all()
    ]

    return {
        "missed_days": missed_days,
        "streak_before": streak_before,
        "today_date": today.isoformat(),
        "overdue_tasks": overdue,
        "missed_habits": [],
        "current_level": 1,
    }
