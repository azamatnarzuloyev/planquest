"""Redis cache layer for AI responses."""

import json
import logging

from app.core.redis import get_redis

logger = logging.getLogger(__name__)


async def get_cached(key: str) -> dict | None:
    """Get cached AI response."""
    redis = get_redis()
    data = await redis.get(key)
    if data:
        logger.debug(f"AI cache hit: {key}")
        return json.loads(data)
    return None


async def set_cached(key: str, data: dict, ttl: int = 14400) -> None:
    """Cache AI response. Default TTL: 4 hours."""
    redis = get_redis()
    await redis.setex(key, ttl, json.dumps(data, ensure_ascii=False, default=str))
    logger.debug(f"AI cache set: {key} ttl={ttl}s")


async def invalidate_cached(pattern: str) -> int:
    """Invalidate cached responses matching pattern."""
    redis = get_redis()
    keys = []
    async for key in redis.scan_iter(match=pattern):
        keys.append(key)
    if keys:
        await redis.delete(*keys)
        logger.info(f"AI cache invalidated: {len(keys)} keys matching {pattern}")
    return len(keys)
