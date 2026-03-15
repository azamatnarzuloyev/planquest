from datetime import date, timedelta
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.habit import HabitLog
from app.models.task import Task


async def get_weekly_completion(db: AsyncSession, user_id: UUID) -> list[dict]:
    """Get daily task completion counts for last 7 days."""
    today = date.today()
    days = []

    for i in range(6, -1, -1):
        d = today - timedelta(days=i)

        # Tasks completed on this day
        result = await db.execute(
            select(func.count()).where(
                Task.user_id == user_id,
                func.date(Task.completed_at) == d,
                Task.status == "completed",
            )
        )
        task_count = result.scalar_one()

        # Habits logged on this day
        result2 = await db.execute(
            select(func.count()).where(
                HabitLog.user_id == user_id,
                HabitLog.date == d,
                HabitLog.completed == True,
            )
        )
        habit_count = result2.scalar_one()

        day_names = ["Du", "Se", "Cho", "Pa", "Ju", "Sha", "Ya"]
        weekday = d.weekday()

        days.append({
            "date": d.isoformat(),
            "day": day_names[weekday],
            "tasks": task_count,
            "habits": habit_count,
            "total": task_count + habit_count,
            "is_today": d == today,
        })

    return days


async def get_total_stats(db: AsyncSession, user_id: UUID) -> dict:
    """Get all-time totals."""
    # Total tasks completed
    tasks_result = await db.execute(
        select(func.count()).where(
            Task.user_id == user_id,
            Task.status == "completed",
        )
    )
    total_tasks = tasks_result.scalar_one()

    # Total habits logged
    habits_result = await db.execute(
        select(func.count()).where(
            HabitLog.user_id == user_id,
            HabitLog.completed == True,
        )
    )
    total_habits = habits_result.scalar_one()

    return {
        "total_tasks_completed": total_tasks,
        "total_habits_logged": total_habits,
    }
