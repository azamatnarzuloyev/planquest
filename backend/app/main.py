import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes.achievements import router as achievements_router
from app.api.routes.ai import router as ai_router
from app.api.routes.auth import router as auth_router
from app.api.routes.cards import router as cards_router
from app.api.routes.chests import router as chests_router
from app.api.routes.focus import router as focus_router
from app.api.routes.goals import router as goals_router
from app.api.routes.habits import router as habits_router
from app.api.routes.health import router as health_router
from app.api.routes.missions import router as missions_router
from app.api.routes.referrals import router as referrals_router
from app.api.routes.reviews import router as reviews_router
from app.api.routes.streaks import router as streaks_router
from app.api.routes.tasks import router as tasks_router
from app.api.routes.telegram import router as telegram_router
from app.api.routes.users import router as users_router
from app.api.routes.wallet import router as wallet_router
from app.config import settings
from app.core.redis import close_redis, init_redis

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    await init_redis()

    # Register domain event handlers
    from app.services.event_handlers import register_all_handlers
    register_all_handlers()

    # Initialize bot
    from app.core.bot import create_bot_and_dispatcher

    bot, dp = create_bot_and_dispatcher()
    if bot is not None:
        from app.bot.setup import set_webhook

        try:
            await set_webhook()
            logger.info("Bot initialized with webhook")
        except Exception as e:
            logger.warning(f"Webhook setup failed (bot still works for API): {e}")
    else:
        logger.warning("Bot not initialized (no BOT_TOKEN)")

    yield

    # Shutdown
    from app.bot.setup import close_bot, delete_webhook

    await delete_webhook()
    await close_bot()
    await close_redis()


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    lifespan=lifespan,
)

from app.core.rate_limit import RateLimitMiddleware
app.add_middleware(RateLimitMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Global exception handler
from fastapi import Request
from fastapi.responses import JSONResponse


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.exception(f"Unhandled error: {request.method} {request.url.path}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Ichki xatolik yuz berdi. Iltimos keyinroq urinib ko'ring."},
    )


app.include_router(health_router)
app.include_router(achievements_router)
app.include_router(ai_router)
app.include_router(auth_router)
app.include_router(cards_router)
app.include_router(chests_router)
app.include_router(users_router)
app.include_router(tasks_router)
app.include_router(habits_router)
app.include_router(focus_router)
app.include_router(goals_router)
app.include_router(streaks_router)
app.include_router(missions_router)
app.include_router(referrals_router)
app.include_router(reviews_router)
app.include_router(wallet_router)
app.include_router(telegram_router)
