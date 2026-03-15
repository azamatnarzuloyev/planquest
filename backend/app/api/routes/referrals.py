from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.services.referral_service import get_referral_stats

router = APIRouter(prefix="/api/referrals", tags=["referrals"])


@router.get("")
async def referral_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get user's referral stats."""
    return await get_referral_stats(db, user.id)
