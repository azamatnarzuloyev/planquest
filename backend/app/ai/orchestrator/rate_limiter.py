"""Redis-based rate limiter for AI calls. Premium users only."""

import logging
from datetime import date
from uuid import UUID

from app.config import settings
from app.core.redis import get_redis

logger = logging.getLogger(__name__)


async def check_rate_limit(user_id: UUID) -> tuple[bool, int, int]:
    """Check if user has remaining AI calls today.

    Returns: (allowed, used, limit)
    """
    limit = settings.AI_DAILY_LIMIT
    key = f"ai:rate:{user_id}:{date.today().isoformat()}"

    redis = get_redis()
    used = await redis.get(key)
    used = int(used) if used else 0

    if used >= limit:
        return False, used, limit

    return True, used, limit


async def increment_rate(user_id: UUID) -> int:
    """Increment AI call count for today. Returns new count."""
    key = f"ai:rate:{user_id}:{date.today().isoformat()}"
    redis = get_redis()
    count = await redis.incr(key)

    # Set TTL on first call (expire at end of day — 24h max)
    if count == 1:
        await redis.expire(key, 86400)

    return count
