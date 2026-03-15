"""Simple per-user API rate limiting via Redis."""

import logging
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse

logger = logging.getLogger(__name__)

MAX_REQUESTS_PER_MINUTE = 100


class RateLimitMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip health checks and static
        if request.url.path.startswith("/health") or request.url.path.startswith("/docs"):
            return await call_next(request)

        # Extract user identifier from JWT (if present)
        auth = request.headers.get("authorization", "")
        if not auth.startswith("Bearer "):
            return await call_next(request)

        token = auth[7:]
        # Use token hash as rate limit key (quick, no JWT decode needed)
        key = f"ratelimit:{hash(token) % 1000000}"

        try:
            from app.core.redis import redis_client
            if redis_client:
                count = await redis_client.incr(key)
                if count == 1:
                    await redis_client.expire(key, 60)
                if count > MAX_REQUESTS_PER_MINUTE:
                    return JSONResponse(
                        status_code=429,
                        content={"detail": "Juda ko'p so'rov. 1 daqiqa kuting."},
                    )
        except Exception:
            pass  # Don't fail requests if Redis is down

        return await call_next(request)
