from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.database import async_session
from app.services.goal_service import get_goals

router = Router(name="goal_commands")


@router.message(Command("goals"))
async def cmd_goals(message: Message, user=None) -> None:
    """Show user's active goals."""
    if user is None:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    async with async_session() as db:
        goals = await get_goals(db, user.id)

    if not goals:
        await message.answer(
            "🎯 Hali maqsad yo'q.\n\n"
            "Mini App'da Goals bo'limidan yangi maqsad qo'shing!"
        )
        return

    text = "🎯 <b>Maqsadlar</b>\n\n"
    for g in goals:
        level_icon = {"yearly": "🏆", "monthly": "📅", "weekly": "📋"}.get(g.level, "📌")
        bar_filled = int(g.progress_percent / 10)
        bar_empty = 10 - bar_filled
        bar = "█" * bar_filled + "░" * bar_empty
        text += (
            f"{level_icon} <b>{g.title}</b>\n"
            f"   [{bar}] {g.progress_percent:.0f}%\n"
            f"   {g.linked_tasks_done}/{g.linked_tasks_total} task\n\n"
        )

    await message.answer(text)
