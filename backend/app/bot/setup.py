import logging

from app.config import settings
from app.core.bot import get_bot

logger = logging.getLogger(__name__)


async def set_webhook() -> None:
    """Register webhook URL with Telegram."""
    if not settings.WEBHOOK_URL:
        logger.info("WEBHOOK_URL not set — skipping webhook registration")
        return

    bot = get_bot()
    await bot.set_webhook(
        url=settings.WEBHOOK_URL,
        drop_pending_updates=True,
    )
    logger.info(f"Webhook set to: {settings.WEBHOOK_URL}")


async def delete_webhook() -> None:
    """Remove webhook from Telegram."""
    try:
        bot = get_bot()
        await bot.delete_webhook()
        logger.info("Webhook deleted")
    except RuntimeError:
        pass


async def close_bot() -> None:
    """Close bot session."""
    try:
        bot = get_bot()
        await bot.session.close()
        logger.info("Bot session closed")
    except RuntimeError:
        pass
