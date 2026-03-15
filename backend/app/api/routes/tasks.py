from datetime import date, datetime, timezone
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.task import TaskCreate, TaskResponse, TaskUpdate
from app.schemas.xp import TaskCompleteResponse
from app.services.task_service import (
    archive_task,
    create_task,
    get_task_by_id,
    get_tasks,
    update_task,
)
from app.services.streak_service import update_streak
from app.services.xp_service import award_xp, calculate_task_xp

router = APIRouter(prefix="/api/tasks", tags=["tasks"])


@router.post("", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task_endpoint(
    data: TaskCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Create a new task."""
    task = await create_task(db, user.id, data)
    return TaskResponse.model_validate(task)


@router.get("", response_model=list[TaskResponse])
async def list_tasks(
    planned_date: date | None = Query(default=None, alias="date"),
    task_status: str | None = Query(default=None, alias="status"),
    priority: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[TaskResponse]:
    """List tasks with optional filters."""
    tasks = await get_tasks(
        db=db,
        user_id=user.id,
        planned_date=planned_date,
        status=task_status,
        priority=priority,
        limit=limit,
        offset=offset,
    )
    return [TaskResponse.model_validate(t) for t in tasks]


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Get a single task by ID."""
    task = await get_task_by_id(db, task_id, user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    return TaskResponse.model_validate(task)


@router.patch("/{task_id}", response_model=TaskResponse)
async def update_task_endpoint(
    task_id: UUID,
    data: TaskUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskResponse:
    """Update a task."""
    task = await get_task_by_id(db, task_id, user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    updated = await update_task(db, task, data)
    return TaskResponse.model_validate(updated)


@router.post("/{task_id}/complete", response_model=TaskCompleteResponse)
async def complete_task(
    task_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> TaskCompleteResponse:
    """Complete a task and award XP."""
    task = await get_task_by_id(db, task_id, user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    if task.status == "completed":
        raise HTTPException(status_code=400, detail="Task already completed")
    if task.status == "archived":
        raise HTTPException(status_code=400, detail="Cannot complete archived task")

    # Calculate and award XP
    xp_amount = calculate_task_xp(task)
    xp_result = await award_xp(db, user.id, "task", task.id, xp_amount)

    # Update streak
    streak_result = await update_streak(db, user.id, "activity")

    # Update mission progress
    from app.services.mission_service import update_mission_progress
    await update_mission_progress(db, user.id, "tasks_completed", 1)

    # Check achievements
    from app.services.achievement_service import check_achievements
    await check_achievements(db, user.id, "tasks_completed", 1)

    # Update task
    task.status = "completed"
    task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
    task.xp_awarded = xp_result["xp_awarded"]
    await db.commit()
    await db.refresh(task)

    return TaskCompleteResponse(
        task=TaskResponse.model_validate(task),
        xp_awarded=xp_result["xp_awarded"],
        total_xp=xp_result["total_xp"],
        leveled_up=xp_result["leveled_up"],
        new_level=xp_result["new_level"],
        coins_earned=xp_result["coins_earned"],
    )


@router.delete("/{task_id}")
async def delete_task(
    task_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Archive a task (soft delete)."""
    task = await get_task_by_id(db, task_id, user.id)
    if task is None:
        raise HTTPException(status_code=404, detail="Task not found")
    await archive_task(db, task)
    return {"ok": True}
