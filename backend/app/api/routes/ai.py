"""AI API routes — Premium only."""

import logging
from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from uuid import UUID

from app.api.deps import get_current_user
from app.ai.mappers.goal_mapper import map_decomposition_to_tasks
from app.ai.mappers.plan_mapper import map_suggested_tasks
from app.ai.schemas.goals import GoalDecomposition
from app.ai.schemas.plans import DailyPlan
from app.ai.services.ai_service import ai_health, call_agent, check_premium
from app.ai.tools.analytics import get_analytics_summary, get_recovery_context
from app.ai.tools.context import build_planner_context
from app.ai.validators.plan_validator import validate_plan
from app.core.database import get_db
from app.models.user import User
from app.services.goal_service import get_goal_by_id
from app.services.task_service import create_task
from app.services.xp_service import get_or_create_progress

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


@router.get("/health")
async def ai_health_check():
    """Check AI system health (public)."""
    return await ai_health()


# === Pre-planning Questions ===


@router.get("/questions")
async def get_planning_questions(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get personalized pre-planning questions. Premium only."""
    check_premium(user)

    # Build light context for question generation
    from app.services.task_service import get_tasks
    from app.services.habit_service import get_habits
    from app.services.streak_service import get_user_streaks
    from app.services.focus_service import get_focus_stats

    today = date.today()
    pending = await get_tasks(db, user.id, planned_date=today, status="pending")
    all_pending = await get_tasks(db, user.id, status="pending")
    overdue = [t for t in all_pending if t.planned_date < today]
    habits = await get_habits(db, user.id, filter_today=True)
    streaks = await get_user_streaks(db, user.id)
    focus = await get_focus_stats(db, user.id)
    activity = next((s for s in streaks if s.type == "activity"), None)

    # Calculate missed days
    missed_days = 0
    if activity and activity.last_active_date:
        missed_days = max(0, (today - activity.last_active_date).days - 1)

    days_since_reg = (today - user.created_at.date()).days if user.created_at else 0

    context = {
        "first_name": user.first_name,
        "segment": user.segment or "other",
        "main_intent": user.main_intent or "routine",
        "current_level": 1,
        "streak_current": activity.current_count if activity else 0,
        "pending_count": len(pending),
        "overdue_count": len(overdue),
        "habits_done": 0,
        "habits_total": len(habits),
        "missed_days": missed_days,
        "days_since_reg": days_since_reg,
        "focus_today": focus.get("today_minutes", 0),
    }

    result = await call_agent(
        request_type="questions",
        user_id=user.id,
        context=context,
        db=db,
        cache_key=f"ai:questions:{user.id}:{today.isoformat()}",
        cache_ttl=7200,  # 2 hours
    )

    return result


# === Conversational Planner ===


class ChatMessage(BaseModel):
    role: str  # "user" or "assistant"
    content: str


class ChatPlanRequest(BaseModel):
    messages: list[ChatMessage]
    force_plan: bool = False  # If true, AI must return plan immediately


@router.post("/chat-plan")
async def chat_plan_endpoint(
    body: ChatPlanRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Conversational AI planner — chat-style. Premium only."""
    check_premium(user)

    # Build user context
    context = await build_planner_context(db, user.id, user)

    # Call conversational planner
    from app.ai.agents.conversational_planner import chat_plan
    from app.ai.orchestrator.rate_limiter import check_rate_limit, increment_rate

    allowed, used, limit = await check_rate_limit(user.id)
    if not allowed:
        from fastapi import HTTPException
        raise HTTPException(status_code=429, detail=f"Kunlik limit tugadi ({used}/{limit})")

    messages = [{"role": m.role, "content": m.content} for m in body.messages]
    result, metadata = await chat_plan(messages, context, force_plan=body.force_plan)

    await increment_rate(user.id)

    # Log
    from app.ai.models.ai_request_log import AIRequestLog
    log = AIRequestLog(
        user_id=user.id, agent="chat_plan", model=metadata.get("model", ""),
        input_tokens=metadata.get("input_tokens", 0),
        output_tokens=metadata.get("output_tokens", 0),
        latency_ms=metadata.get("latency_ms", 0), status="success",
    )
    db.add(log)
    await db.commit()

    return {"response": result, "usage": {"used": used + 1, "limit": limit}}


# === Plan Generation ===


class PlanResponse(BaseModel):
    plan: dict
    validation: dict
    cached: bool = False
    usage: dict = {}


class PlanGenerateRequest(BaseModel):
    focus: str | None = None       # "Bugun nimaga fokus qilasiz?"
    available_time: str | None = None  # "Qancha vaqtingiz bor?"
    energy: str | None = None      # "Kayfiyatingiz qanday?"


class PlanApplyRequest(BaseModel):
    plan: dict
    apply_suggested: bool = True


class PlanApplyResponse(BaseModel):
    tasks_created: int
    message: str


@router.post("/plan", response_model=PlanResponse)
async def generate_plan(
    body: PlanGenerateRequest | None = None,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanResponse:
    """Generate an AI daily plan with optional user answers. Premium only."""
    check_premium(user)

    # Build context
    context = await build_planner_context(db, user.id, user)

    # Add user answers to context
    if body:
        if body.focus:
            context["user_focus"] = body.focus
        if body.available_time:
            context["user_available_time"] = body.available_time
        if body.energy:
            context["user_energy"] = body.energy

    # Call AI — no cache if user provided custom answers
    today_str = date.today().isoformat()
    has_custom = body and (body.focus or body.available_time or body.energy)
    cache_key = None if has_custom else f"ai:plan:{user.id}:{today_str}"

    result = await call_agent(
        request_type="daily_plan",
        user_id=user.id,
        context=context,
        db=db,
        cache_key=cache_key,
        cache_ttl=14400,  # 4 hours
    )

    # Validate plan
    plan_data = result["data"]
    plan = DailyPlan.model_validate(plan_data)
    is_valid, errors, warnings = validate_plan(plan)

    return PlanResponse(
        plan=plan_data,
        validation={"valid": is_valid, "errors": errors, "warnings": warnings},
        cached=result.get("cached", False),
        usage=result.get("usage", {}),
    )


@router.post("/plan/apply", response_model=PlanApplyResponse)
async def apply_plan(
    body: PlanApplyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> PlanApplyResponse:
    """Apply an AI-generated plan — create suggested tasks. Premium only."""
    check_premium(user)

    created = 0
    plan = DailyPlan.model_validate(body.plan)
    today = date.today()

    # Validate
    is_valid, errors, _ = validate_plan(plan)
    if not is_valid:
        raise HTTPException(status_code=400, detail=f"Invalid plan: {errors}")

    # 1. Create tasks from time_blocks (new tasks — no ref_id)
    for block in plan.time_blocks:
        if block.type == "task" and not block.ref_id:
            # Parse duration from time block
            try:
                sh, sm = map(int, block.start.split(":"))
                eh, em = map(int, block.end.split(":"))
                minutes = (eh * 60 + em) - (sh * 60 + sm)
            except (ValueError, AttributeError):
                minutes = 30

            from app.schemas.task import TaskCreate as TC
            await create_task(db, user.id, TC(
                title=block.title,
                planned_date=today,
                priority="medium",
                difficulty="medium",
                estimated_minutes=max(5, min(180, minutes)),
                source="ai_plan",
            ))
            created += 1

    # 2. Create suggested_new_tasks
    if body.apply_suggested:
        task_creates = map_suggested_tasks(plan, today)
        for tc in task_creates:
            tc.source = "ai_plan"
            await create_task(db, user.id, tc)
            created += 1

    await db.commit()

    return PlanApplyResponse(
        tasks_created=created,
        message=f"{created} ta yangi task yaratildi" if created > 0 else "Hech narsa yaratilmadi",
    )


# === Goal Decomposition ===


class DecomposeResponse(BaseModel):
    decomposition: dict
    cached: bool = False
    usage: dict = {}


class DecomposeApplyRequest(BaseModel):
    decomposition: dict
    goal_id: str


class DecomposeApplyResponse(BaseModel):
    tasks_created: int
    weeks: int
    message: str


@router.post("/goals/{goal_id}/decompose", response_model=DecomposeResponse)
async def decompose_goal(
    goal_id: UUID,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DecomposeResponse:
    """AI goal decomposition into milestones and tasks. Premium only."""
    check_premium(user)

    goal = await get_goal_by_id(db, goal_id, user.id)
    if goal is None:
        raise HTTPException(status_code=404, detail="Goal not found")

    progress = await get_or_create_progress(db, user.id)

    context = {
        "goal_title": goal.title,
        "goal_description": goal.description,
        "target_date": goal.target_date.isoformat() if goal.target_date else None,
        "category": goal.category,
        "segment": user.segment,
        "current_level": progress.current_level,
        "avg_tasks_per_day": 3,
    }

    cache_key = f"ai:decompose:{goal_id}"
    result = await call_agent(
        request_type="goal_breakdown",
        user_id=user.id,
        context=context,
        db=db,
        cache_key=cache_key,
        cache_ttl=86400,  # 24 hours
    )

    return DecomposeResponse(
        decomposition=result["data"],
        cached=result.get("cached", False),
        usage=result.get("usage", {}),
    )


@router.post("/goals/decompose/apply", response_model=DecomposeApplyResponse)
async def apply_decomposition(
    body: DecomposeApplyRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> DecomposeApplyResponse:
    """Apply goal decomposition — create tasks linked to goal. Premium only."""
    check_premium(user)

    decomp = GoalDecomposition.model_validate(body.decomposition)
    task_items = map_decomposition_to_tasks(decomp, body.goal_id)

    created = 0
    for item in task_items:
        tc = item["task_create"]
        task = await create_task(db, user.id, tc)
        # Link task to goal
        task.goal_id = UUID(body.goal_id) if isinstance(body.goal_id, str) else body.goal_id
        created += 1

    await db.commit()

    return DecomposeApplyResponse(
        tasks_created=created,
        weeks=decomp.total_weeks,
        message=f"{created} ta task {decomp.total_weeks} hafta uchun yaratildi",
    )


# === Recovery ===


@router.post("/recover")
async def recovery_plan(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Generate AI recovery plan after missed days. Premium only."""
    check_premium(user)

    context = await get_recovery_context(db, user.id)
    context["current_level"] = (await get_or_create_progress(db, user.id)).current_level

    if context["missed_days"] <= 0:
        return {"data": None, "message": "Siz hech kun o'tkazib yubormadingiz!"}

    result = await call_agent(
        request_type="recovery",
        user_id=user.id,
        context=context,
        db=db,
        cache_key=f"ai:recover:{user.id}:{date.today().isoformat()}",
        cache_ttl=7200,
    )
    return result


# === Coaching ===


@router.get("/coach")
async def coaching_insights(
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> dict:
    """Get AI coaching insights based on 14-day analytics. Premium only."""
    check_premium(user)

    analytics = await get_analytics_summary(db, user.id, days=14)
    progress = await get_or_create_progress(db, user.id)

    context = {
        "segment": user.segment,
        "current_level": progress.current_level,
        "analytics": analytics,
        "weekly_breakdown": analytics.get("weekly_breakdown", []),
    }

    result = await call_agent(
        request_type="coaching",
        user_id=user.id,
        context=context,
        db=db,
        cache_key=f"ai:coach:{user.id}:{date.today().isocalendar()[1]}",
        cache_ttl=86400,
    )
    return result
