from datetime import date
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_current_user
from app.core.database import get_db
from app.models.user import User
from app.schemas.focus import (
    FocusEndResponse,
    FocusSessionResponse,
    FocusStartRequest,
    FocusStatsResponse,
)
from app.services.focus_service import (
    DAILY_FOCUS_XP_CAP,
    calculate_focus_xp,
    end_session,
    get_active_session,
    get_daily_focus_xp,
    get_focus_stats,
    get_planned_duration,
    get_session_history,
    start_session,
)
from app.services.streak_service import update_streak
from app.services.xp_service import award_xp

router = APIRouter(prefix="/api/focus", tags=["focus"])


@router.post("/start", response_model=FocusSessionResponse, status_code=201)
async def start_focus(
    data: FocusStartRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FocusSessionResponse:
    """Start a new focus session."""
    # Check for active session
    active = await get_active_session(db, user.id)
    if active is not None:
        raise HTTPException(status_code=400, detail="A focus session is already active")

    planned = get_planned_duration(data.mode.value, data.planned_duration)
    session = await start_session(db, user.id, data.mode.value, planned, data.task_id)
    return FocusSessionResponse.model_validate(session)


@router.post("/{session_id}/end", response_model=FocusEndResponse)
async def end_focus(
    session_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FocusEndResponse:
    """End an active focus session."""
    active = await get_active_session(db, user.id)
    if active is None or active.id != session_id:
        raise HTTPException(status_code=404, detail="Active session not found")

    session = await end_session(db, active)

    # Calculate and award XP
    xp_amount = calculate_focus_xp(session.mode, session.planned_duration, session.actual_duration)

    xp_result = {"xp_awarded": 0, "total_xp": 0, "leveled_up": False, "new_level": 0}
    if xp_amount > 0 and session.status == "completed":
        # Check daily focus XP cap
        daily_xp = await get_daily_focus_xp(db, user.id)
        remaining = max(0, DAILY_FOCUS_XP_CAP - daily_xp)
        capped_xp = min(xp_amount, remaining)

        if capped_xp > 0:
            xp_result = await award_xp(db, user.id, "focus", session.id, capped_xp)
            session.xp_awarded = xp_result["xp_awarded"]

        # Update streaks
        await update_streak(db, user.id, "activity")
        await update_streak(db, user.id, "focus")

        # Update mission progress
        from app.services.mission_service import update_mission_progress
        await update_mission_progress(db, user.id, "focus_sessions", 1)
        await update_mission_progress(db, user.id, "focus_minutes", session.actual_duration)

        # Check achievements
        from app.services.achievement_service import check_achievements
        await check_achievements(db, user.id, "focus_sessions", 1)
        await check_achievements(db, user.id, "focus_minutes", session.actual_duration)

    await db.commit()
    await db.refresh(session)

    return FocusEndResponse(
        session=FocusSessionResponse.model_validate(session),
        xp_awarded=xp_result["xp_awarded"],
        total_xp=xp_result["total_xp"],
        leveled_up=xp_result["leveled_up"],
        new_level=xp_result["new_level"],
    )


@router.get("/active", response_model=FocusSessionResponse | None)
async def get_active(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Get currently active focus session, or null."""
    session = await get_active_session(db, user.id)
    if session is None:
        return None
    return FocusSessionResponse.model_validate(session)


@router.get("/history", response_model=list[FocusSessionResponse])
async def focus_history(
    from_date: date | None = Query(default=None, alias="from"),
    to_date: date | None = Query(default=None, alias="to"),
    limit: int = Query(default=50, ge=1, le=100),
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> list[FocusSessionResponse]:
    """Get focus session history."""
    sessions = await get_session_history(db, user.id, from_date, to_date, limit)
    return [FocusSessionResponse.model_validate(s) for s in sessions]


@router.get("/stats", response_model=FocusStatsResponse)
async def focus_stats(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> FocusStatsResponse:
    """Get focus statistics."""
    stats = await get_focus_stats(db, user.id)
    return FocusStatsResponse(**stats)
