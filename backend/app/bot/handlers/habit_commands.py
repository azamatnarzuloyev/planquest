import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.core.database import async_session
from app.schemas.habit import HabitLogCreate
from app.services.habit_service import get_habit_by_id, get_habit_log, get_habits, log_habit, get_habit_xp
from app.services.streak_service import update_streak
from app.services.xp_service import award_xp

logger = logging.getLogger(__name__)
router = Router(name="habit_commands")


@router.message(Command("habits"))
async def cmd_habits(message: Message, user=None) -> None:
    """Show today's habits with inline buttons."""
    if user is None:
        await message.answer("Avval /start bosing.")
        return

    async with async_session() as db:
        habits = await get_habits(db, user.id)

    if not habits:
        await message.answer(
            "🔄 <b>Hali habit yo'q.</b>\n\n"
            "Dashboard orqali habit qo'shing!"
        )
        return

    today = date.today()
    text = f"🔄 <b>Bugungi habitlar ({len(habits)} ta):</b>\n\n"
    buttons = []

    for habit in habits[:10]:
        async with async_session() as db:
            today_log = await get_habit_log(db, habit.id, user.id, today)

        if today_log and today_log.completed:
            text += f"  ✅ {habit.icon} {habit.title}\n"
        else:
            text += f"  ⬜ {habit.icon} {habit.title}\n"
            buttons.append([
                InlineKeyboardButton(
                    text=f"✅ {habit.icon} {habit.title}",
                    callback_data=f"habit_done:{habit.id}",
                ),
            ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons) if buttons else None
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("habit_done:"))
async def callback_habit_done(callback_query: CallbackQuery, user=None) -> None:
    """Log a habit from inline button."""
    habit_id = callback_query.data.split(":")[1]

    if user is None:
        await callback_query.answer("Xatolik yuz berdi")
        return

    from uuid import UUID

    async with async_session() as db:
        habit = await get_habit_by_id(db, UUID(habit_id), user.id)
        if habit is None:
            await callback_query.answer("Habit topilmadi")
            return

        log, is_new = await log_habit(db, habit, HabitLogCreate(value=habit.target_value))

        xp_awarded = 0
        if is_new and log.completed:
            xp_amount = get_habit_xp(habit.type)
            xp_result = await award_xp(db, user.id, "habit", habit.id, xp_amount)
            xp_awarded = xp_result["xp_awarded"]
            await update_streak(db, user.id, "activity")
            await update_streak(db, user.id, f"habit_{habit.id}")
            await db.commit()

    if xp_awarded > 0:
        await callback_query.answer(f"✅ +{xp_awarded} XP! 🎉")
    else:
        await callback_query.answer("✅ Bajarildi!")
