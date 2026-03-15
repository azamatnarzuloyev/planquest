import logging

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from app.core.database import async_session
from app.services.focus_service import get_active_session, start_session, get_planned_duration

logger = logging.getLogger(__name__)
router = Router(name="focus_commands")


@router.message(Command("focus"))
async def cmd_focus(message: Message, user=None) -> None:
    """Start a focus session: /focus or /focus 50"""
    if user is None:
        await message.answer("Avval /start bosing.")
        return

    args = message.text.split()
    minutes = 25  # default pomodoro
    mode = "pomodoro_25"

    if len(args) > 1:
        try:
            minutes = int(args[1])
            if minutes <= 0 or minutes > 180:
                await message.answer("⏱ Vaqt 1-180 minut orasida bo'lishi kerak.")
                return
            if minutes <= 25:
                mode = "pomodoro_25"
            elif minutes <= 50:
                mode = "deep_50"
            elif minutes <= 90:
                mode = "ultra_90"
            else:
                mode = "custom"
        except ValueError:
            await message.answer("⏱ <code>/focus 25</code> yoki <code>/focus 50</code> formatida yozing.")
            return

    planned = get_planned_duration(mode, minutes if mode == "custom" else None)

    async with async_session() as db:
        active = await get_active_session(db, user.id)
        if active is not None:
            elapsed = "faol"
            await message.answer(
                f"⏱ <b>Fokus session allaqachon {elapsed}!</b>\n\n"
                f"Mode: {active.mode} | {active.planned_duration} min\n\n"
                "Tugatish uchun Dashboard'ni oching."
            )
            return

        session = await start_session(db, user.id, mode, planned, None)

    mode_names = {
        "pomodoro_25": "Pomodoro (25 min)",
        "deep_50": "Deep Work (50 min)",
        "ultra_90": "Ultra Focus (90 min)",
        "custom": f"Custom ({planned} min)",
    }

    await message.answer(
        f"🎯 <b>Fokus session boshlandi!</b>\n\n"
        f"⏱ {mode_names.get(mode, mode)}\n\n"
        "Diqqatingizni jamlang va vazifalaringizni bajaring.\n"
        "Tugatish uchun Dashboard'ni oching."
    )
