import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.database import async_session
from app.services.focus_service import get_focus_stats
from app.services.streak_service import get_user_streaks
from app.services.task_service import get_tasks
from app.services.xp_service import get_or_create_progress, get_xp_for_next_level

logger = logging.getLogger(__name__)
router = Router(name="stats_commands")


@router.message(Command("stats"))
async def cmd_stats(message: Message, user=None) -> None:
    """Show user stats: level, XP, streak, today's score."""
    if user is None:
        await message.answer("Avval /start bosing.")
        return

    async with async_session() as db:
        progress = await get_or_create_progress(db, user.id)
        await db.commit()

        streaks = await get_user_streaks(db, user.id)
        activity_streak = next((s for s in streaks if s.type == "activity"), None)

        today_tasks = await get_tasks(db, user.id, planned_date=date.today())
        completed = sum(1 for t in today_tasks if t.status == "completed")
        total = len(today_tasks)

        focus = await get_focus_stats(db, user.id)

    next_level_xp = get_xp_for_next_level(progress.current_level)
    streak_count = activity_streak.current_count if activity_streak else 0
    streak_emoji = "🔥" if streak_count > 0 else "❄️"

    score = f"{completed}/{total}" if total > 0 else "0/0"

    text = (
        f"📊 <b>Statistika</b>\n\n"
        f"⭐ Level: <b>{progress.current_level}</b>\n"
        f"✨ XP: <b>{progress.total_xp}</b> / {next_level_xp}\n"
        f"🪙 Coinlar: <b>{progress.coins_balance}</b>\n\n"
        f"{streak_emoji} Streak: <b>{streak_count} kun</b>\n"
        f"📋 Bugun: <b>{score}</b> task\n"
        f"⏱ Fokus: <b>{focus['today_minutes']}</b> min bugun\n"
    )

    await message.answer(text)
