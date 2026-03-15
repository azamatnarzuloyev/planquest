"""Convert validated AI plan into backend-ready task create requests."""

from datetime import date

from app.ai.schemas.plans import DailyPlan, SuggestedTask
from app.schemas.task import TaskCreate


def map_suggested_tasks(plan: DailyPlan, target_date: date) -> list[TaskCreate]:
    """Convert AI suggested tasks into TaskCreate objects."""
    results = []
    for st in plan.suggested_new_tasks:
        results.append(TaskCreate(
            title=st.title,
            planned_date=target_date,
            priority=st.priority,
            difficulty=st.difficulty,
            estimated_minutes=st.estimated_minutes,
        ))
    return results
