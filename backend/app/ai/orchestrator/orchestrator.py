"""Central orchestrator — routes requests, manages rate limits, logs calls."""

import logging
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.ai.models.ai_request_log import AIRequestLog
from app.ai.orchestrator.rate_limiter import check_rate_limit, increment_rate
from app.ai.orchestrator.router import get_agent
from app.ai.providers.cache import get_cached, set_cached

logger = logging.getLogger(__name__)


class AIOrchestrator:
    """Main entry point for all AI requests."""

    async def handle(
        self,
        request_type: str,
        user_id: UUID,
        context: dict,
        db: AsyncSession,
        cache_key: str | None = None,
        cache_ttl: int = 14400,
    ) -> dict:
        """Handle an AI request.

        Args:
            request_type: Agent type (daily_plan, goal_breakdown, etc.)
            user_id: User UUID
            context: Data context for the agent
            db: Database session for logging
            cache_key: Optional cache key
            cache_ttl: Cache TTL in seconds (default 4h)

        Returns:
            {"data": validated_output, "cached": bool, "usage": metadata}

        Raises:
            RateLimitError: If user exceeded daily limit
            ValueError: If agent not found
            RuntimeError: If AI call fails
        """
        # 1. Check rate limit
        allowed, used, limit = await check_rate_limit(user_id)
        if not allowed:
            raise RateLimitExceeded(used, limit)

        # 2. Check cache
        if cache_key:
            cached = await get_cached(cache_key)
            if cached:
                await self._log_request(db, user_id, request_type, cached=True)
                await db.commit()
                return {"data": cached, "cached": True, "usage": {"used": used, "limit": limit}}

        # 3. Get agent and run
        agent = get_agent(request_type)

        try:
            result, metadata = await agent.run(context)
            status = "success"
        except Exception as e:
            status = "error"
            await self._log_request(
                db, user_id, request_type,
                status=status, error=str(e),
            )
            await db.commit()
            raise

        # 4. Increment rate limit
        await increment_rate(user_id)

        # 5. Log request
        await self._log_request(
            db, user_id, request_type,
            status=status,
            model=metadata.get("model", ""),
            input_tokens=metadata.get("input_tokens", 0),
            output_tokens=metadata.get("output_tokens", 0),
            latency_ms=metadata.get("latency_ms", 0),
            retry_count=metadata.get("retry_count", 0),
        )

        # 6. Commit log
        await db.commit()

        # 7. Cache result
        result_dict = result.model_dump() if hasattr(result, "model_dump") else result
        if cache_key:
            await set_cached(cache_key, result_dict, cache_ttl)

        return {
            "data": result_dict,
            "cached": False,
            "usage": {
                "used": used + 1,
                "limit": limit,
                **metadata,
            },
        }

    async def _log_request(
        self,
        db: AsyncSession,
        user_id: UUID,
        agent: str,
        status: str = "success",
        model: str = "",
        input_tokens: int = 0,
        output_tokens: int = 0,
        latency_ms: int = 0,
        cached: bool = False,
        retry_count: int = 0,
        error: str | None = None,
    ) -> None:
        """Log AI request to database."""
        try:
            log = AIRequestLog(
                user_id=user_id,
                agent=agent,
                model=model,
                input_tokens=input_tokens,
                output_tokens=output_tokens,
                latency_ms=latency_ms,
                status=status,
                cached=cached,
                retry_count=retry_count,
            )
            db.add(log)
            await db.flush()
        except Exception as e:
            logger.error(f"Failed to log AI request: {e}")


class RateLimitExceeded(Exception):
    def __init__(self, used: int, limit: int):
        self.used = used
        self.limit = limit
        super().__init__(f"AI rate limit exceeded: {used}/{limit}")


# Singleton
_orchestrator: AIOrchestrator | None = None


def get_orchestrator() -> AIOrchestrator:
    global _orchestrator
    if _orchestrator is None:
        _orchestrator = AIOrchestrator()
    return _orchestrator
