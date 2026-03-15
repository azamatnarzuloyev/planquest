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
        referral_code = args[1][4:]
        if user:
            try:
                from app.services.referral_service import create_referral
                async with async_session() as db:
                    await create_referral(db, referral_code, user.id)
                    # Also set referred_by on user
                    db_user = await get_user_by_telegram_id(db, user.telegram_id)
                    if db_user and db_user.referred_by is None:
                        from app.models.user import User as UserModel
                        from sqlalchemy import select
                        ref = await db.execute(select(UserModel).where(UserModel.referral_code == referral_code))
                        referrer = ref.scalar_one_or_none()
                        if referrer and referrer.id != user.id:
                            db_user.referred_by = referrer.id
                    await db.commit()
            except Exception:
                pass  # Don't fail start command on referral error

    name = user.first_name if user else (message.from_user.first_name or "")

    # New user or incomplete onboarding → start onboarding
    if user is None or user.onboarding_step < 6:
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
            from app.bot.handlers.onboarding import get_intent_keyboard
            await message.answer("📌 <b>Bot sizga nimada yordam bersin?</b>", reply_markup=get_intent_keyboard())
        elif step == 2:
            await message.answer(
                "⏰ <b>Kuningiz qanday o'tadi?</b>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🌅 Erta (6-7)", callback_data="ob_rhy_early")],
                    [InlineKeyboardButton(text="☀️ O'rtacha (8-9)", callback_data="ob_rhy_normal")],
                    [InlineKeyboardButton(text="🌙 Kechroq (10+)", callback_data="ob_rhy_late")],
                    [InlineKeyboardButton(text="🔄 Turlicha", callback_data="ob_rhy_mixed")],
                ]),
            )
        elif step == 3:
            await message.answer(
                "📊 <b>Qanchalik reja xohlaysiz?</b>",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🟢 Yengil (2-3 task)", callback_data="ob_com_easy")],
                    [InlineKeyboardButton(text="🟡 O'rtacha (4-5 task)", callback_data="ob_com_medium")],
                    [InlineKeyboardButton(text="🔴 Faol (5-7 task)", callback_data="ob_com_hard")],
                ]),
            )
        elif step == 4:
            await message.answer(
                "🎯 <b>Asosiy maqsadingiz nima?</b>\n\n"
                "Hozir erishmoqchi bo'lgan narsani yozing:"
            )
        elif step == 5:
            await message.answer(
                "Oxirgi qadam!",
                reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                    [InlineKeyboardButton(text="🚀 Boshlash!", callback_data="ob_finish")],
                ]),
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


@router.message(Command("invite"))
async def cmd_invite(message: Message, user=None, **kwargs) -> None:
    """Show referral link and stats."""
    if user is None:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    from app.services.referral_service import get_referral_stats
    async with async_session() as db:
        stats = await get_referral_stats(db, user.id)

    code = stats["referral_code"]
    link = f"https://t.me/planAIbot?start=ref_{code}"

    text = (
        f"📨 <b>Do'stlaringizni taklif qiling!</b>\n\n"
        f"Sizning havolangiz:\n<code>{link}</code>\n\n"
        f"📊 Statistika:\n"
        f"  Taklif qilingan: {stats['total_referred']}/{stats['max_referrals']}\n"
        f"  Aktivlashgan: {stats['activated']}\n\n"
        f"🎁 Mukofotlar:\n"
        f"  Referrer: +{100} XP, +{50} 🪙\n"
        f"  Taklif qilingan: +{50} 🪙"
    )
    await message.answer(text)


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
