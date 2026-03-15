from datetime import date

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.mission import MissionResponse
from app.services.mission_service import generate_daily_missions, generate_weekly_missions, get_missions

router = APIRouter(prefix="/api/missions", tags=["missions"])


@router.get("", response_model=list[MissionResponse])
async def list_missions(
    type: str = Query(default="daily", regex="^(daily|weekly)$"),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[MissionResponse]:
    """Get missions. Auto-generates if none exist for today/this week."""
    today = date.today()

    missions = await get_missions(db, user.id, type, today)

    # Auto-generate if empty
    if not missions:
        if type == "daily":
            missions = await generate_daily_missions(db, user.id, today)
        else:
            missions = await generate_weekly_missions(db, user.id, today)
        await db.commit()

    return [MissionResponse.model_validate(m) for m in missions]
