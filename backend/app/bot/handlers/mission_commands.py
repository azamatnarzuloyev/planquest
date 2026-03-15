from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.database import async_session
from app.services.mission_service import generate_daily_missions, generate_weekly_missions, get_missions

router = Router(name="mission_commands")


@router.message(Command("missions"))
async def cmd_missions(message: Message, user=None) -> None:
    """Show today's missions."""
    if user is None:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    from datetime import date

    today = date.today()

    async with async_session() as db:
        daily = await get_missions(db, user.id, "daily", today)
        if not daily:
            daily = await generate_daily_missions(db, user.id, today)
            await db.commit()

        weekly = await get_missions(db, user.id, "weekly", today)
        if not weekly:
            weekly = await generate_weekly_missions(db, user.id, today)
            await db.commit()

    # Format daily
    text = "🎯 <b>Bugungi missiyalar</b>\n\n"
    for m in daily:
        if m.status == "completed":
            icon = "✅"
        else:
            icon = {"easy": "🟢", "medium": "🟡", "stretch": "🔴"}.get(m.difficulty, "⚪")
        progress = f"{m.current_value}/{m.target_value}"
        reward = f"+{m.reward_xp}XP +{m.reward_coins}🪙"
        text += f"{icon} {m.title} [{progress}] {reward}\n"

    # Format weekly
    text += "\n📅 <b>Haftalik missiyalar</b>\n\n"
    for m in weekly:
        icon = "✅" if m.status == "completed" else "📌"
        progress = f"{m.current_value}/{m.target_value}"
        reward = f"+{m.reward_xp}XP +{m.reward_coins}🪙"
        text += f"{icon} {m.title} [{progress}] {reward}\n"

    await message.answer(text)
