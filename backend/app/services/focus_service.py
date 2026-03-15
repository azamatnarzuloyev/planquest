import math
from datetime import date, datetime, timedelta, timezone
from uuid import UUID

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.focus_session import FocusSession

# Mode → default duration
MODE_DURATION = {
    "pomodoro_25": 25,
    "deep_50": 50,
    "ultra_90": 90,
}

# Mode → base XP
MODE_XP = {
    "pomodoro_25": 15,
    "deep_50": 30,
    "ultra_90": 50,
}

DAILY_FOCUS_XP_CAP = 200


def get_planned_duration(mode: str, custom_duration: int | None) -> int:
    if mode == "custom" and custom_duration:
        return custom_duration
    return MODE_DURATION.get(mode, 25)


def calculate_focus_xp(mode: str, planned_duration: int, actual_duration: int) -> int:
    """Calculate XP for a focus session."""
    ratio = actual_duration / planned_duration if planned_duration > 0 else 0

    # Less than 50% → no XP
    if ratio < 0.5:
        return 0

    if mode == "custom":
        base_xp = math.floor(planned_duration * 0.6)
    else:
        base_xp = MODE_XP.get(mode, 15)

    # Partial completion → proportional XP
    if ratio < 1.0:
        return math.floor(base_xp * ratio)

    return base_xp


async def get_active_session(db: AsyncSession, user_id: UUID) -> FocusSession | None:
    result = await db.execute(
        select(FocusSession).where(
            FocusSession.user_id == user_id,
            FocusSession.status == "active",
        )
    )
    return result.scalar_one_or_none()


async def start_session(
    db: AsyncSession, user_id: UUID, mode: str, planned_duration: int, task_id: UUID | None
) -> FocusSession:
    session = FocusSession(
        user_id=user_id,
        task_id=task_id,
        mode=mode,
        planned_duration=planned_duration,
        status="active",
        started_at=datetime.now(timezone.utc).replace(tzinfo=None),
    )
    db.add(session)
    await db.commit()
    await db.refresh(session)
    return session


async def end_session(db: AsyncSession, session: FocusSession) -> FocusSession:
    """End a focus session and calculate actual duration."""
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    actual_minutes = int((now - session.started_at).total_seconds() / 60)

    # Cap at planned duration + 5 min buffer
    actual_minutes = min(actual_minutes, session.planned_duration + 5)

    session.ended_at = now
    session.actual_duration = actual_minutes

    ratio = actual_minutes / session.planned_duration if session.planned_duration > 0 else 0
    session.status = "completed" if ratio >= 0.5 else "abandoned"

    await db.flush()
    return session


async def get_session_history(
    db: AsyncSession, user_id: UUID,
    from_date: date | None = None, to_date: date | None = None,
    limit: int = 50,
) -> list[FocusSession]:
    query = select(FocusSession).where(
        FocusSession.user_id == user_id,
        FocusSession.status != "active",
    )
    if from_date:
        query = query.where(func.date(FocusSession.started_at) >= from_date)
    if to_date:
        query = query.where(func.date(FocusSession.started_at) <= to_date)
    query = query.order_by(FocusSession.started_at.desc()).limit(limit)
    result = await db.execute(query)
    return list(result.scalars().all())


async def get_focus_stats(db: AsyncSession, user_id: UUID) -> dict:
    """Get focus statistics."""
    today = date.today()
    week_start = today - timedelta(days=today.weekday())  # Monday

    base_filter = and_(
        FocusSession.user_id == user_id,
        FocusSession.status == "completed",
    )

    # Today
    today_result = await db.execute(
        select(
            func.coalesce(func.sum(FocusSession.actual_duration), 0),
            func.count(),
        ).where(base_filter, func.date(FocusSession.started_at) == today)
    )
    today_row = today_result.one()

    # This week
    week_result = await db.execute(
        select(
            func.coalesce(func.sum(FocusSession.actual_duration), 0),
            func.count(),
        ).where(base_filter, func.date(FocusSession.started_at) >= week_start)
    )
    week_row = week_result.one()

    # Total
    total_result = await db.execute(
        select(
            func.coalesce(func.sum(FocusSession.actual_duration), 0),
            func.count(),
        ).where(base_filter)
    )
    total_row = total_result.one()

    return {
        "today_minutes": today_row[0],
        "today_sessions": today_row[1],
        "week_minutes": week_row[0],
        "week_sessions": week_row[1],
        "total_minutes": total_row[0],
        "total_sessions": total_row[1],
    }


async def get_daily_focus_xp(db: AsyncSession, user_id: UUID) -> int:
    """Get total focus XP earned today (for daily cap)."""
    from app.models.xp_event import XpEvent

    result = await db.execute(
        select(func.coalesce(func.sum(XpEvent.xp_amount), 0)).where(
            XpEvent.user_id == user_id,
            XpEvent.source_type == "focus",
            func.date(XpEvent.created_at) == date.today(),
        )
    )
    return result.scalar_one()
