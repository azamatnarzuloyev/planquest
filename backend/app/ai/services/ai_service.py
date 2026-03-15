"""High-level AI service — entry point for all AI features."""

import logging
from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.orchestrator.orchestrator import RateLimitExceeded, get_orchestrator
from app.ai.orchestrator.router import get_available_agents
from app.ai.providers.openai_provider import get_openai_provider

logger = logging.getLogger(__name__)


def check_premium(user) -> None:
    """Raise 403 if user is not premium."""
    if not user.is_premium:
        raise HTTPException(
            status_code=403,
            detail="AI features require Premium subscription",
        )


async def call_agent(
    request_type: str,
    user_id: UUID,
    context: dict,
    db: AsyncSession,
    cache_key: str | None = None,
    cache_ttl: int = 14400,
) -> dict:
    """Call an AI agent through the orchestrator.

    Returns: {"data": ..., "cached": bool, "usage": ...}
    Raises: HTTPException on rate limit or error
    """
    orchestrator = get_orchestrator()

    try:
        result = await orchestrator.handle(
            request_type=request_type,
            user_id=user_id,
            context=context,
            db=db,
            cache_key=cache_key,
            cache_ttl=cache_ttl,
        )
        return result

    except RateLimitExceeded as e:
        raise HTTPException(
            status_code=429,
            detail=f"Kunlik AI limit tugadi ({e.used}/{e.limit}). Ertaga qayta urinib ko'ring.",
        )

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        logger.exception(f"AI agent error: {request_type}")
        raise HTTPException(
            status_code=503,
            detail="AI hozir ishlamayapti. Keyinroq urinib ko'ring.",
        )


async def ai_health() -> dict:
    """Check AI system health."""
    provider = get_openai_provider()
    provider_ok = await provider.health_check()
    agents = get_available_agents()

    return {
        "provider": "ok" if provider_ok else "unavailable",
        "registered_agents": agents,
        "api_key_set": bool(provider.client),
    }
