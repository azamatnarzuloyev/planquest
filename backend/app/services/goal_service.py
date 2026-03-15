"""Goal CRUD and progress calculation."""

from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.goal import Goal
from app.models.task import Task
from app.schemas.goal import GoalCreate, GoalUpdate


async def create_goal(db: AsyncSession, user_id: UUID, data: GoalCreate) -> Goal:
    goal = Goal(
        user_id=user_id,
        title=data.title,
        description=data.description,
        category=data.category,
        level=data.level.value,
        target_date=data.target_date,
        parent_goal_id=data.parent_goal_id,
    )
    db.add(goal)
    await db.commit()
    await db.refresh(goal)
    return goal


async def get_goals(db: AsyncSession, user_id: UUID, status: str = "active") -> list[Goal]:
    result = await db.execute(
        select(Goal)
        .where(and_(Goal.user_id == user_id, Goal.status == status))
        .order_by(Goal.created_at.desc())
    )
    return list(result.scalars().all())


async def get_goal_by_id(db: AsyncSession, goal_id: UUID, user_id: UUID) -> Goal | None:
    result = await db.execute(
        select(Goal).where(and_(Goal.id == goal_id, Goal.user_id == user_id))
    )
    return result.scalar_one_or_none()


async def update_goal(db: AsyncSession, goal: Goal, data: GoalUpdate) -> Goal:
    for field, value in data.model_dump(exclude_unset=True).items():
        if hasattr(value, "value"):
            value = value.value
        setattr(goal, field, value)
    await db.commit()
    await db.refresh(goal)
    return goal


async def archive_goal(db: AsyncSession, goal: Goal) -> Goal:
    goal.status = "archived"
    await db.commit()
    await db.refresh(goal)
    return goal


async def update_goal_progress(db: AsyncSession, goal_id: UUID, user_id: UUID) -> None:
    """Recalculate goal progress from linked tasks."""
    total = await db.execute(
        select(func.count()).where(and_(Task.goal_id == goal_id, Task.user_id == user_id, Task.status != "archived"))
    )
    done = await db.execute(
        select(func.count()).where(and_(Task.goal_id == goal_id, Task.user_id == user_id, Task.status == "completed"))
    )
    total_count = total.scalar_one()
    done_count = done.scalar_one()

    goal = await get_goal_by_id(db, goal_id, user_id)
    if goal:
        goal.linked_tasks_total = total_count
        goal.linked_tasks_done = done_count
        goal.progress_percent = round((done_count / total_count * 100), 1) if total_count > 0 else 0
        if goal.progress_percent >= 100 and goal.status == "active":
            goal.status = "completed"
        await db.flush()
