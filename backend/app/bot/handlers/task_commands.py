import logging
from datetime import date, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.core.database import async_session
from app.schemas.task import TaskCreate
from app.services.task_service import create_task, get_task_by_id, get_tasks
from app.services.xp_service import award_xp, calculate_task_xp
from app.services.streak_service import update_streak

logger = logging.getLogger(__name__)
router = Router(name="task_commands")


def _parse_date(text: str) -> date:
    """Parse date from user input."""
    text = text.strip().lower()
    if text in ("bugun", "today", ""):
        return date.today()
    if text in ("ertaga", "tomorrow"):
        return date.today() + timedelta(days=1)
    try:
        return date.fromisoformat(text)
    except ValueError:
        return date.today()


@router.message(Command("add"))
async def cmd_add(message: Message, user=None) -> None:
    """Create a task: /add Buy groceries tomorrow"""
    if user is None:
        await message.answer("Avval /start bosing.")
        return

    args = message.text.split(maxsplit=1)
    if len(args) < 2 or not args[1].strip():
        await message.answer(
            "📝 <b>Task qo'shish:</b>\n\n"
            "<code>/add Vazifa nomi</code>\n"
            "<code>/add Vazifa nomi ertaga</code>\n"
            "<code>/add Vazifa nomi 2026-03-20</code>"
        )
        return

    raw = args[1].strip()

    # Try to extract date from last word
    parts = raw.rsplit(maxsplit=1)
    title = raw
    planned = date.today()

    if len(parts) == 2:
        possible_date = parts[1].lower()
        if possible_date in ("bugun", "today", "ertaga", "tomorrow") or len(possible_date) == 10:
            title = parts[0]
            planned = _parse_date(possible_date)

    if len(title) < 3:
        await message.answer("❌ Vazifa nomi kamida 3 ta belgidan iborat bo'lishi kerak.")
        return

    async with async_session() as db:
        task = await create_task(db, user.id, TaskCreate(
            title=title,
            planned_date=planned,
            source="bot",
        ))

    await message.answer(
        f"✅ <b>Task yaratildi:</b>\n\n"
        f"📌 {task.title}\n"
        f"📅 {task.planned_date}\n\n"
        f"+10 XP birinchi task uchun! 🎮"
    )


@router.message(Command("today"))
async def cmd_today(message: Message, user=None) -> None:
    """Show today's tasks with inline buttons."""
    if user is None:
        await message.answer("Avval /start bosing.")
        return

    async with async_session() as db:
        tasks = await get_tasks(db, user.id, planned_date=date.today(), status="pending")

    if not tasks:
        await message.answer(
            "📋 <b>Bugungi rejada task yo'q.</b>\n\n"
            "Task qo'shish: /add Vazifa nomi"
        )
        return

    text = f"📋 <b>Bugungi reja ({len(tasks)} ta):</b>\n\n"
    buttons = []

    for i, task in enumerate(tasks[:10], 1):
        priority_icon = {"critical": "🔴", "high": "🟠", "medium": "🟡", "low": "⚪"}.get(task.priority, "⚪")
        text += f"{i}. {priority_icon} {task.title}\n"
        buttons.append([
            InlineKeyboardButton(text=f"✅ {i}. Bajarildi", callback_data=f"task_done:{task.id}"),
            InlineKeyboardButton(text=f"⏰ Ertaga", callback_data=f"task_tomorrow:{task.id}"),
        ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer(text, reply_markup=keyboard)


@router.callback_query(lambda c: c.data and c.data.startswith("task_done:"))
async def callback_task_done(callback_query: CallbackQuery, user=None) -> None:
    """Complete a task from inline button."""
    task_id = callback_query.data.split(":")[1]

    if user is None:
        await callback_query.answer("Xatolik yuz berdi")
        return

    from datetime import datetime, timezone
    from uuid import UUID

    async with async_session() as db:
        task = await get_task_by_id(db, UUID(task_id), user.id)
        if task is None or task.status != "pending":
            await callback_query.answer("Task topilmadi yoki allaqachon bajarilgan")
            return

        xp_amount = calculate_task_xp(task)
        xp_result = await award_xp(db, user.id, "task", task.id, xp_amount)
        await update_streak(db, user.id, "activity")

        task.status = "completed"
        task.completed_at = datetime.now(timezone.utc).replace(tzinfo=None)
        task.xp_awarded = xp_result["xp_awarded"]
        await db.commit()

    await callback_query.answer(f"+{xp_result['xp_awarded']} XP! 🎉")

    # Edit original message to show completion
    try:
        old_text = callback_query.message.text or callback_query.message.html_text or ""
        await callback_query.message.edit_text(
            old_text + f"\n\n✅ <b>{task.title}</b> — Bajarildi! +{xp_result['xp_awarded']} XP",
            reply_markup=None,
        )
    except Exception:
        pass


@router.callback_query(lambda c: c.data and c.data.startswith("task_tomorrow:"))
async def callback_task_tomorrow(callback_query: CallbackQuery, user=None) -> None:
    """Reschedule task to tomorrow."""
    task_id = callback_query.data.split(":")[1]

    if user is None:
        await callback_query.answer("Xatolik yuz berdi")
        return

    from uuid import UUID
    from app.schemas.task import TaskUpdate

    async with async_session() as db:
        task = await get_task_by_id(db, UUID(task_id), user.id)
        if task is None:
            await callback_query.answer("Task topilmadi")
            return

        from app.services.task_service import update_task
        await update_task(db, task, TaskUpdate(planned_date=date.today() + timedelta(days=1)))

    await callback_query.answer("⏰ Ertaga surildi")
