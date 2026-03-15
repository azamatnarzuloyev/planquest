import logging
from datetime import date, time

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.core.database import async_session
from app.schemas.task import TaskCreate
from app.schemas.user import UserSettingsUpdate, UserUpdate
from app.services.task_service import create_task
from app.services.user_service import get_user_by_id, update_user, update_user_settings
from app.services.xp_service import award_xp

logger = logging.getLogger(__name__)
router = Router(name="onboarding")

# Onboarding steps:
# 0 = not started (new user)
# 1 = segment selected, waiting for first task text
# 2 = first task created, waiting for reminder time
# 3 = reminder set, waiting for confirmation
# 4 = onboarding complete


# === Step 1: Segment Selection ===

SEGMENTS = {
    "ob_student": ("student", "🎓 Talaba"),
    "ob_freelancer": ("freelancer", "💻 Freelancer"),
    "ob_entrepreneur": ("entrepreneur", "🚀 Tadbirkor"),
    "ob_developer": ("developer", "👨‍💻 Dasturchi"),
    "ob_other": ("other", "👤 Boshqa"),
}


def get_segment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎓 Talaba", callback_data="ob_student"),
            InlineKeyboardButton(text="💻 Freelancer", callback_data="ob_freelancer"),
        ],
        [
            InlineKeyboardButton(text="🚀 Tadbirkor", callback_data="ob_entrepreneur"),
            InlineKeyboardButton(text="👨‍💻 Dasturchi", callback_data="ob_developer"),
        ],
        [
            InlineKeyboardButton(text="👤 Boshqa", callback_data="ob_other"),
        ],
    ])


@router.callback_query(lambda c: c.data and c.data.startswith("ob_") and c.data in SEGMENTS)
async def callback_segment(callback_query: CallbackQuery, user=None) -> None:
    """Step 1: User selects their segment."""
    if user is None:
        await callback_query.answer("Xatolik")
        return

    segment_key = callback_query.data
    segment_value, segment_label = SEGMENTS[segment_key]

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            await update_user(db, db_user, UserUpdate(segment=segment_value))
            # Move to step 1 (waiting for first task)
            db_user.onboarding_step = 1
            await db.commit()

    await callback_query.answer(f"{segment_label} tanlandi!")

    # Step 2: Ask for first task
    await callback_query.message.edit_text(
        f"Ajoyib! Siz — {segment_label}\n\n"
        "📝 <b>Endi birinchi vazifangizni yarating!</b>\n\n"
        "Bugun nima qilmoqchisiz? Oddiy yozing:\n"
        "<i>Masalan: \"Kitob o'qish\" yoki \"Loyiha taqdimoti tayyorlash\"</i>"
    )


# === Step 2: First Task (handled as regular message) ===


@router.message(lambda message: True)
async def handle_onboarding_message(message: Message, user=None) -> None:
    """
    Catch text messages during onboarding.
    Only processes if user is in onboarding step 1 (waiting for first task).
    """
    if user is None or user.onboarding_step != 1:
        return  # Not in onboarding, let other handlers process

    text = message.text
    if not text or text.startswith("/"):
        return  # Skip commands

    title = text.strip()
    if len(title) < 3:
        await message.answer("Vazifa nomi kamida 3 ta belgi bo'lishi kerak. Qayta yozing:")
        return

    if len(title) > 200:
        title = title[:200]

    # Create the first task
    async with async_session() as db:
        task = await create_task(db, user.id, TaskCreate(
            title=title,
            planned_date=date.today(),
            source="bot",
        ))
        # Award bonus XP for first task
        xp_result = await award_xp(db, user.id, "task", task.id, 10)

        # Move to step 2 (reminder time)
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            db_user.onboarding_step = 2
            await db.commit()

    # Step 3: Ask for reminder time
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🌅 07:00", callback_data="ob_time_07"),
            InlineKeyboardButton(text="☀️ 08:00", callback_data="ob_time_08"),
        ],
        [
            InlineKeyboardButton(text="🌤 09:00", callback_data="ob_time_09"),
            InlineKeyboardButton(text="🕙 10:00", callback_data="ob_time_10"),
        ],
    ])

    await message.answer(
        f"✅ <b>Vazifa yaratildi:</b> {title}\n"
        f"📅 Bugungi reja uchun\n"
        f"✨ +10 XP!\n\n"
        "⏰ <b>Ertalabki eslatma qachon kelsin?</b>",
        reply_markup=keyboard,
    )


# === Step 3: Reminder Time ===

REMINDER_TIMES = {
    "ob_time_07": (time(7, 0), "07:00"),
    "ob_time_08": (time(8, 0), "08:00"),
    "ob_time_09": (time(9, 0), "09:00"),
    "ob_time_10": (time(10, 0), "10:00"),
}


@router.callback_query(lambda c: c.data and c.data.startswith("ob_time_"))
async def callback_reminder_time(callback_query: CallbackQuery, user=None) -> None:
    """Step 3: User selects morning reminder time."""
    if user is None:
        await callback_query.answer("Xatolik")
        return

    time_key = callback_query.data
    if time_key not in REMINDER_TIMES:
        await callback_query.answer("Noto'g'ri vaqt")
        return

    reminder_time, time_label = REMINDER_TIMES[time_key]

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            await update_user_settings(
                db, db_user,
                UserSettingsUpdate(morning_reminder_time=reminder_time),
            )
            db_user.onboarding_step = 4  # Onboarding complete
            await db.commit()

    await callback_query.answer("Sozlandi!")

    from app.config import settings
    from aiogram.types import WebAppInfo

    keyboard_buttons = []
    mini_app_url = settings.MINI_APP_URL or (settings.WEBHOOK_URL.rsplit("/api/", 1)[0] if settings.WEBHOOK_URL else "")
    if mini_app_url:
        keyboard_buttons.append([
            InlineKeyboardButton(
                text="📊 Dashboard ochish",
                web_app=WebAppInfo(url=mini_app_url),
            )
        ])
    keyboard_buttons.append([
        InlineKeyboardButton(text="📋 Bugungi reja", callback_data="cmd_today"),
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await callback_query.message.edit_text(
        "🎉 <b>Hammasi tayyor!</b>\n\n"
        f"⏰ Har kuni soat {time_label} da ertalabki reja keladi.\n"
        "Vazifalarni bajaring, streaklar yig'ing va level oshiring!\n\n"
        "📊 <b>Hozirgi holat:</b>\n"
        "⭐ Level 1 | ✨ 10 XP | 🔥 0 kun streak\n\n"
        "Omad! 💪",
        reply_markup=keyboard,
    )
