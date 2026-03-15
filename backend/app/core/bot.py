import logging

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode

from app.config import settings

logger = logging.getLogger(__name__)

bot: Bot | None = None
dp: Dispatcher | None = None


def get_bot() -> Bot:
    if bot is None:
        raise RuntimeError("Bot not initialized")
    return bot


def get_dispatcher() -> Dispatcher:
    if dp is None:
        raise RuntimeError("Dispatcher not initialized")
    return dp


def create_bot_and_dispatcher() -> tuple[Bot, Dispatcher]:
    """Create Bot and Dispatcher instances."""
    global bot, dp

    if not settings.BOT_TOKEN or settings.BOT_TOKEN == "your_bot_token_here":
        logger.warning("BOT_TOKEN not set — bot will not work")
        return None, None

    bot = Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )
    dp = Dispatcher()

    # Register middlewares
    from app.bot.middlewares.auth import AuthMiddleware

    dp.message.middleware(AuthMiddleware())
    dp.callback_query.middleware(AuthMiddleware())

    # Register routers (order matters — commands first, onboarding last as catch-all)
    from app.bot.handlers.commands import router as commands_router
    from app.bot.handlers.task_commands import router as task_router
    from app.bot.handlers.habit_commands import router as habit_router
    from app.bot.handlers.focus_commands import router as focus_router
    from app.bot.handlers.stats_commands import router as stats_router
    from app.bot.handlers.mission_commands import router as mission_router
    from app.bot.handlers.goal_commands import router as goal_cmd_router
    from app.bot.handlers.ai_commands import router as ai_cmd_router
    from app.bot.handlers.onboarding import router as onboarding_router

    dp.include_router(commands_router)
    dp.include_router(task_router)
    dp.include_router(habit_router)
    dp.include_router(focus_router)
    dp.include_router(stats_router)
    dp.include_router(mission_router)
    dp.include_router(goal_cmd_router)
    dp.include_router(ai_cmd_router)
    dp.include_router(onboarding_router)  # Last — catches free text for onboarding

    logger.info("Bot and Dispatcher created successfully")
    return bot, dp
