import logging
from typing import Any, Awaitable, Callable

from aiogram import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject

from app.core.database import async_session
from app.services.user_service import get_or_create_user

logger = logging.getLogger(__name__)


class AuthMiddleware(BaseMiddleware):
    """
    Middleware that auto-registers users and injects User object into handlers.

    For every incoming message/callback:
    1. Extract telegram user from update
    2. Find or create user in database
    3. Pass user object to handler via data["user"]
    """

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Extract telegram user from event
        tg_user = None
        if isinstance(event, Message) and event.from_user:
            tg_user = event.from_user
        elif isinstance(event, CallbackQuery) and event.from_user:
            tg_user = event.from_user

        if tg_user is None or tg_user.is_bot:
            return await handler(event, data)

        try:
            async with async_session() as db:
                user, is_new = await get_or_create_user(
                    db=db,
                    telegram_id=tg_user.id,
                    first_name=tg_user.first_name or "",
                    last_name=tg_user.last_name,
                    username=tg_user.username,
                )
                data["user"] = user
                if is_new:
                    logger.info(f"New user registered: {tg_user.id} ({tg_user.first_name})")
        except Exception:
            logger.exception(f"Error in auth middleware for user {tg_user.id}")

        return await handler(event, data)
