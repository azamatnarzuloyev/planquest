import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import BufferedInputFile, InlineKeyboardButton, InlineKeyboardMarkup, Message

from sqlalchemy import select

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

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🔥 Streak card", callback_data="share_streak"),
            InlineKeyboardButton(text="⭐ Level card", callback_data="share_level"),
        ],
        [InlineKeyboardButton(text="📊 Haftalik card", callback_data="share_weekly")],
    ])

    await message.answer(text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("share_"))
async def cb_share_card(callback, user=None) -> None:
    """Generate and send a shareable card image."""
    if user is None:
        await callback.answer("Xatolik")
        return

    card_type = callback.data.replace("share_", "")
    await callback.answer("Card yaratilmoqda...")

    try:
        from app.services.cards.generator import generate_streak_card, generate_level_card, generate_weekly_card

        async with async_session() as db:
            if card_type == "streak":
                streaks = await get_user_streaks(db, user.id)
                activity = next((s for s in streaks if s.type == "activity"), None)
                png = generate_streak_card(
                    user.first_name,
                    activity.current_count if activity else 0,
                    activity.best_count if activity else 0,
                )
            elif card_type == "level":
                progress = await get_or_create_progress(db, user.id)
                await db.commit()
                titles = {1: "Yangi boshlovchi", 5: "Beginner", 10: "Rising Star", 20: "Pro", 30: "Deep Worker"}
                title = "Yangi boshlovchi"
                for k in sorted(titles.keys(), reverse=True):
                    if progress.current_level >= k:
                        title = titles[k]
                        break
                png = generate_level_card(user.first_name, progress.current_level, title, progress.total_xp)
            elif card_type == "weekly":
                from datetime import timedelta
                from sqlalchemy import func, and_
                from app.models.task import Task
                from app.models.habit import HabitLog
                from app.models.focus_session import FocusSession

                today = date.today()
                monday = today - timedelta(days=today.weekday())
                tasks_r = await db.execute(select(func.count()).where(and_(Task.user_id == user.id, Task.planned_date >= monday, Task.status == "completed")))
                habits_r = await db.execute(select(func.count()).where(and_(HabitLog.user_id == user.id, HabitLog.date >= monday, HabitLog.completed == True)))
                focus_r = await db.execute(select(func.coalesce(func.sum(FocusSession.actual_duration), 0)).where(and_(FocusSession.user_id == user.id, func.date(FocusSession.started_at) >= monday, FocusSession.status == "completed")))
                from app.models.xp_event import XpEvent
                xp_r = await db.execute(select(func.coalesce(func.sum(XpEvent.xp_amount), 0)).where(and_(XpEvent.user_id == user.id, func.date(XpEvent.created_at) >= monday)))
                streaks = await get_user_streaks(db, user.id)
                activity = next((s for s in streaks if s.type == "activity"), None)

                png = generate_weekly_card(
                    user.first_name, tasks_r.scalar_one(), habits_r.scalar_one(),
                    focus_r.scalar_one(), xp_r.scalar_one(),
                    activity.current_count if activity else 0,
                )
            else:
                await callback.answer("Noma'lum card turi")
                return

        photo = BufferedInputFile(png, filename=f"{card_type}_card.png")
        await callback.message.answer_photo(
            photo,
            caption=f"📊 {user.first_name} — PlanQuest\nt.me/planAIbot",
        )
    except Exception:
        logger.exception(f"Card generation error: {card_type}")
        await callback.message.answer("Card yaratishda xatolik.")
