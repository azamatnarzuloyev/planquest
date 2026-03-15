from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.streak import StreakResponse
from app.services.streak_service import get_user_streaks

router = APIRouter(prefix="/api/streaks", tags=["streaks"])


@router.get("", response_model=list[StreakResponse])
async def list_streaks(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[StreakResponse]:
    """Get all streaks for the current user."""
    streaks = await get_user_streaks(db, user.id)
    return [StreakResponse.model_validate(s) for s in streaks]
