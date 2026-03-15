from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.chest import ChestOpenResponse, ChestResponse
from app.services.chest_service import get_chest_by_id, get_unopened_chests, open_chest

router = APIRouter(prefix="/api/chests", tags=["chests"])


@router.get("", response_model=list[ChestResponse])
async def list_chests(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[ChestResponse]:
    """Get all unopened chests."""
    chests = await get_unopened_chests(db, user.id)
    return [ChestResponse.model_validate(c) for c in chests]


@router.post("/{chest_id}/open", response_model=ChestOpenResponse)
async def open_chest_endpoint(
    chest_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> ChestOpenResponse:
    """Open a chest and receive loot."""
    chest = await get_chest_by_id(db, chest_id, user.id)
    if chest is None:
        raise HTTPException(status_code=404, detail="Chest not found")
    if chest.status == "opened":
        raise HTTPException(status_code=400, detail="Chest already opened")

    loot = await open_chest(db, chest)
    await db.commit()

    return ChestOpenResponse(
        chest=ChestResponse.model_validate(chest),
        loot=loot,
    )
