from datetime import date
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.task import Task
from app.schemas.task import TaskCreate, TaskUpdate


async def create_task(db: AsyncSession, user_id: UUID, data: TaskCreate) -> Task:
    """Create a new task."""
    task = Task(
        user_id=user_id,
        title=data.title,
        notes=data.notes,
        planned_date=data.planned_date,
        due_date=data.due_date,
        priority=data.priority.value,
        difficulty=data.difficulty.value,
        estimated_minutes=data.estimated_minutes,
        category=data.category,
        source=data.source.value,
    )
    db.add(task)
    await db.commit()
    await db.refresh(task)
    return task


async def get_task_by_id(db: AsyncSession, task_id: UUID, user_id: UUID) -> Task | None:
    """Get a single task by ID, scoped to user."""
    result = await db.execute(
        select(Task).where(Task.id == task_id, Task.user_id == user_id)
    )
    return result.scalar_one_or_none()


async def get_tasks(
    db: AsyncSession,
    user_id: UUID,
    planned_date: date | None = None,
    status: str | None = None,
    priority: str | None = None,
    limit: int = 50,
    offset: int = 0,
) -> list[Task]:
    """Get tasks for a user with optional filters."""
    query = select(Task).where(Task.user_id == user_id)

    if planned_date:
        query = query.where(Task.planned_date == planned_date)
    if status:
        query = query.where(Task.status == status)
    else:
        # Default: exclude archived
        query = query.where(Task.status != "archived")
    if priority:
        query = query.where(Task.priority == priority)

    query = query.order_by(Task.planned_date.asc(), Task.created_at.asc())
    query = query.limit(limit).offset(offset)

    result = await db.execute(query)
    return list(result.scalars().all())


async def update_task(db: AsyncSession, task: Task, data: TaskUpdate) -> Task:
    """Update task fields."""
    update_data = data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        if hasattr(value, "value"):  # enum
            value = value.value
        setattr(task, field, value)
    await db.commit()
    await db.refresh(task)
    return task


async def archive_task(db: AsyncSession, task: Task) -> Task:
    """Soft delete — set status to archived."""
    task.status = "archived"
    await db.commit()
    await db.refresh(task)
    return task
