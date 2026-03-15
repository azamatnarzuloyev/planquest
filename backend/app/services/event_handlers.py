"""Domain event handlers — side effects triggered by core events."""

import logging

from app.core.events import (
    ACHIEVEMENT_UNLOCKED,
    LEVEL_UP,
    STREAK_MILESTONE,
    on,
)

logger = logging.getLogger(__name__)


@on(ACHIEVEMENT_UNLOCKED)
async def notify_achievement(user_telegram_id: int, name: str, icon: str, xp: int, coins: int, **kwargs):
    """Send bot notification when achievement is unlocked."""
    try:
        from app.core.bot import bot as bot_instance
        if bot_instance is None:
            return
        text = (
            f"🏆 <b>Yutuq ochildi!</b>\n\n"
            f"{icon} <b>{name}</b>\n"
            f"+{xp} XP, +{coins} 🪙"
        )
        await bot_instance.send_message(chat_id=user_telegram_id, text=text, parse_mode="HTML")
    except Exception:
        logger.exception("Achievement notification failed")


@on(LEVEL_UP)
async def notify_level_up(user_telegram_id: int, new_level: int, coins_earned: int, **kwargs):
    """Send bot notification on level up."""
    try:
        from app.core.bot import bot as bot_instance
        if bot_instance is None:
            return
        text = (
            f"⭐ <b>Level UP!</b>\n\n"
            f"Siz <b>Level {new_level}</b> ga chiqdingiz!\n"
            f"+{coins_earned} 🪙"
        )
        await bot_instance.send_message(chat_id=user_telegram_id, text=text, parse_mode="HTML")
    except Exception:
        logger.exception("Level up notification failed")


@on(STREAK_MILESTONE)
async def notify_streak_milestone(user_telegram_id: int, streak_count: int, coins: int, **kwargs):
    """Send bot notification on streak milestone."""
    try:
        from app.core.bot import bot as bot_instance
        if bot_instance is None:
            return
        text = (
            f"🔥 <b>Streak milestone!</b>\n\n"
            f"<b>{streak_count} kun</b> ketma-ket faol bo'ldingiz!\n"
            f"+{coins} 🪙"
        )
        from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🔥 Share card", callback_data="share_streak")],
        ])
        await bot_instance.send_message(chat_id=user_telegram_id, text=text, parse_mode="HTML", reply_markup=keyboard)
    except Exception:
        logger.exception("Streak milestone notification failed")


def register_all_handlers():
    """Import this module to register all event handlers."""
    logger.info("Domain event handlers registered")
