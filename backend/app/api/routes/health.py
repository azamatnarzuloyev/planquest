from fastapi import APIRouter
from sqlalchemy import text

from app.config import settings
from app.core.database import engine
from app.core.redis import get_redis

router = APIRouter(tags=["health"])


@router.get("/health")
async def health():
    return {
        "status": "ok",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
    }


@router.get("/health/ready")
async def health_ready():
    checks = {"database": "ok", "redis": "ok"}

    # Check database
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
    except Exception as e:
        checks["database"] = f"error: {str(e)}"

    # Check redis
    try:
        redis = get_redis()
        await redis.ping()
    except Exception as e:
        checks["redis"] = f"error: {str(e)}"

    all_ok = all(v == "ok" for v in checks.values())
    return {
        "status": "ok" if all_ok else "degraded",
        **checks,
    }
