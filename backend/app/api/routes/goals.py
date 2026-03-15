from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.goal import GoalCreate, GoalResponse, GoalUpdate
from app.services.goal_service import archive_goal, create_goal, get_goal_by_id, get_goals, update_goal

router = APIRouter(prefix="/api/goals", tags=["goals"])


@router.post("", response_model=GoalResponse, status_code=status.HTTP_201_CREATED)
async def create_goal_endpoint(
    data: GoalCreate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await create_goal(db, user.id, data)
    return GoalResponse.model_validate(goal)


@router.get("", response_model=list[GoalResponse])
async def list_goals(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[GoalResponse]:
    goals = await get_goals(db, user.id)
    return [GoalResponse.model_validate(g) for g in goals]


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await get_goal_by_id(db, goal_id, user.id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    return GoalResponse.model_validate(goal)


@router.patch("/{goal_id}", response_model=GoalResponse)
async def update_goal_endpoint(
    goal_id: UUID,
    data: GoalUpdate,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> GoalResponse:
    goal = await get_goal_by_id(db, goal_id, user.id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    updated = await update_goal(db, goal, data)
    return GoalResponse.model_validate(updated)


@router.delete("/{goal_id}")
async def delete_goal(
    goal_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    goal = await get_goal_by_id(db, goal_id, user.id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")
    await archive_goal(db, goal)
    return {"ok": True}
