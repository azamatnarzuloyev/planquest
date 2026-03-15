import logging

from aiogram.types import Update
from fastapi import APIRouter, Request

import app.core.bot as bot_module

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/telegram", tags=["telegram"])


@router.post("/webhook")
async def telegram_webhook(request: Request) -> dict:
    """Receive Telegram webhook updates."""
    if bot_module.bot is None or bot_module.dp is None:
        logger.warning("Bot not initialized, ignoring webhook update")
        return {"ok": True}

    try:
        data = await request.json()
        update = Update.model_validate(data, context={"bot": bot_module.bot})
        await bot_module.dp.feed_update(bot=bot_module.bot, update=update)
    except Exception:
        logger.exception("Error processing webhook update")

    # Always return 200 to prevent Telegram from retrying
    return {"ok": True}
