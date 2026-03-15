"""Convert AI goal decomposition into backend task creates."""

from datetime import date, timedelta

from app.ai.schemas.goals import GoalDecomposition
from app.schemas.task import TaskCreate


def map_decomposition_to_tasks(
    decomp: GoalDecomposition, goal_id: str, start_date: date | None = None
) -> list[dict]:
    """Convert milestones into task create dicts with planned dates.

    Returns list of {task_create: TaskCreate, week: int, milestone_title: str}
    """
    if start_date is None:
        start_date = date.today()

    # Find next Monday
    days_until_monday = (7 - start_date.weekday()) % 7
    if days_until_monday == 0:
        week_start = start_date
    else:
        week_start = start_date + timedelta(days=days_until_monday)

    results = []

    for milestone in decomp.milestones:
        milestone_start = week_start + timedelta(weeks=milestone.week - 1)

        for task in milestone.tasks:
            planned = milestone_start + timedelta(days=task.day_offset - 1)
            results.append({
                "task_create": TaskCreate(
                    title=task.title,
                    planned_date=planned,
                    difficulty=task.difficulty,
                    estimated_minutes=task.estimated_minutes,
                    source="ai_plan",
                ),
                "goal_id": goal_id,
                "week": milestone.week,
                "milestone_title": milestone.title,
            })

    return results
