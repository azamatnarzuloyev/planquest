from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
    WebAppInfo,
)

from app.bot.handlers.onboarding import get_segment_keyboard
from app.config import settings
from app.core.database import async_session
from app.services.user_service import get_user_by_telegram_id

router = Router(name="commands")


@router.message(CommandStart())
async def cmd_start(message: Message, user=None) -> None:
    """Handle /start — route to onboarding or welcome back."""
    # Handle deep link referral: /start ref_XXXXXX
    args = message.text.split()
    if len(args) > 1 and args[1].startswith("ref_"):
        referral_code = args[1][4:]  # Extract code after "ref_"
        if user:
            async with async_session() as db:
                from app.models.user import User
                from sqlalchemy import select

                referrer = await db.execute(
                    select(User).where(User.referral_code == referral_code)
                )
                referrer_user = referrer.scalar_one_or_none()
                if referrer_user and referrer_user.id != user.id:
                    db_user = await get_user_by_telegram_id(db, user.telegram_id)
                    if db_user and db_user.referred_by is None:
                        db_user.referred_by = referrer_user.id
                        await db.commit()

    name = user.first_name if user else (message.from_user.first_name or "")

    # New user or incomplete onboarding → start onboarding
    if user is None or user.onboarding_step < 4:
        step = user.onboarding_step if user else 0

        if step == 0:
            # Step 1: Segment selection
            await message.answer(
                f"👋 <b>Salom, {name}! PlanQuest'ga xush kelibsiz!</b>\n\n"
                "Men sizga kunlik rejalaringizni boshqarishda, "
                "odatlar shakllantirishda va fokus qilishda yordam beraman.\n\n"
                "🎮 Har bir bajarilgan vazifa uchun XP olasiz, "
                "levellar oshirasiz va yutuqlarga erishasiz!\n\n"
                "Avval, siz haqingizda biroz bilib olishim kerak:\n"
                "<b>Siz kimsiz?</b>",
                reply_markup=get_segment_keyboard(),
            )
        elif step == 1:
            # Waiting for first task
            await message.answer(
                "📝 <b>Birinchi vazifangizni yozing!</b>\n\n"
                "Bugun nima qilmoqchisiz?\n"
                "<i>Masalan: \"Kitob o'qish\" yoki \"Loyiha ustida ishlash\"</i>"
            )
        elif step == 2:
            # Waiting for reminder time
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
                "⏰ <b>Ertalabki eslatma qachon kelsin?</b>",
                reply_markup=keyboard,
            )
        return

    # Returning user — welcome back
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
        InlineKeyboardButton(text="❓ Yordam", callback_data="help"),
    ])

    keyboard = InlineKeyboardMarkup(inline_keyboard=keyboard_buttons)

    await message.answer(
        f"👋 <b>Qaytib kelganingizdan xursandman, {name}!</b>\n\n"
        "Bugun nimalarni rejalashtirdingiz?",
        reply_markup=keyboard,
    )


HELP_TEXT = (
    "📋 <b>PlanQuest buyruqlari:</b>\n\n"
    "/add [vazifa] — Task qo'shish\n"
    "/today — Bugungi reja\n"
    "/habits — Habitlar\n"
    "/focus [min] — Fokus session\n"
    "/stats — Statistika\n"
    "/help — Yordam\n\n"
    "💡 <i>Ko'proq imkoniyatlar uchun Dashboard'ni oching!</i>"
)


@router.message(Command("help"))
async def cmd_help(message: Message, **kwargs) -> None:
    await message.answer(HELP_TEXT)


@router.callback_query(lambda c: c.data == "help")
async def callback_help(callback_query: CallbackQuery, **kwargs) -> None:
    await callback_query.answer()
    await callback_query.message.answer(HELP_TEXT)


@router.callback_query(lambda c: c.data == "cmd_today")
async def callback_today(callback_query: CallbackQuery, user=None, **kwargs) -> None:
    """Redirect to /today command."""
    await callback_query.answer()
    if user:
        from app.bot.handlers.task_commands import cmd_today
        await cmd_today(callback_query.message, user=user)


@router.callback_query(lambda c: c.data == "cmd_habits")
async def callback_habits(callback_query: CallbackQuery, user=None, **kwargs) -> None:
    """Redirect to /habits command."""
    await callback_query.answer()
    if user:
        from app.bot.handlers.habit_commands import cmd_habits
        await cmd_habits(callback_query.message, user=user)
