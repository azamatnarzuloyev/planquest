"""6-step onboarding with 4-layer profiling for Uzbekistan market."""

import logging
from datetime import date, time

from aiogram import Router
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from app.core.database import async_session
from app.schemas.goal import GoalCreate
from app.schemas.user import UserSettingsUpdate, UserUpdate
from app.services.goal_service import create_goal
from app.services.user_service import get_user_by_id, update_user, update_user_settings
from app.services.xp_service import award_xp

logger = logging.getLogger(__name__)
router = Router(name="onboarding")

# Onboarding steps:
# 0 = not started → Step A: Life Segment
# 1 = segment set → Step B: Main Intent
# 2 = intent set → Step C: Daily Rhythm
# 3 = rhythm set → Step D: Commitment Level
# 4 = commitment set → Step E: Maqsadingiz (goal text)
# 5 = goal written → Step F: Reminder time + finish
# 6 = onboarding complete


# ============================================================
# Step A: Life Segment — "Hayotingizdagi asosiy rolingiz?"
# ============================================================

SEGMENTS = {
    "ob_seg_student":      ("student",      "🎓 Talaba / abituriyent"),
    "ob_seg_worker":       ("worker",       "💼 Ishchi / ofis xodimi"),
    "ob_seg_freelancer":   ("freelancer",   "💻 Freelancer / remote"),
    "ob_seg_developer":    ("developer",    "👨‍💻 Dasturchi / IT"),
    "ob_seg_entrepreneur": ("entrepreneur", "🛍 Tadbirkor / savdo"),
    "ob_seg_homemaker":    ("homemaker",    "🏠 Uy ishlari / oilaviy"),
    "ob_seg_growth":       ("growth",       "🌱 O'zimni rivojlantirish"),
    "ob_seg_mixed":        ("mixed",        "🔀 Aralash"),
}


def get_segment_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="🎓 Talaba", callback_data="ob_seg_student"),
            InlineKeyboardButton(text="💼 Ishchi", callback_data="ob_seg_worker"),
        ],
        [
            InlineKeyboardButton(text="💻 Freelancer", callback_data="ob_seg_freelancer"),
            InlineKeyboardButton(text="👨‍💻 Dasturchi", callback_data="ob_seg_developer"),
        ],
        [
            InlineKeyboardButton(text="🛍 Tadbirkor", callback_data="ob_seg_entrepreneur"),
            InlineKeyboardButton(text="🏠 Uy ishlari", callback_data="ob_seg_homemaker"),
        ],
        [
            InlineKeyboardButton(text="🌱 O'z rivojlanish", callback_data="ob_seg_growth"),
            InlineKeyboardButton(text="🔀 Aralash", callback_data="ob_seg_mixed"),
        ],
    ])


@router.callback_query(lambda c: c.data and c.data.startswith("ob_seg_"))
async def callback_segment(callback_query: CallbackQuery, user=None) -> None:
    """Step A: Segment selected → go to Step B (Intent)."""
    if user is None:
        await callback_query.answer("Xatolik")
        return

    key = callback_query.data
    if key not in SEGMENTS:
        return

    segment_value, segment_label = SEGMENTS[key]

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            await update_user(db, db_user, UserUpdate(segment=segment_value))
            db_user.onboarding_step = 1
            await db.commit()

    await callback_query.answer(f"{segment_label} ✓")

    # Step B: Main Intent
    await callback_query.message.edit_text(
        f"✅ {segment_label}\n\n"
        "📌 <b>Bot sizga asosan nimada yordam bersin?</b>",
        reply_markup=get_intent_keyboard(),
    )


# ============================================================
# Step B: Main Intent — "Bot nimada yordam bersin?"
# ============================================================

INTENTS = {
    "ob_int_routine":   ("routine",   "✅ Kun tartibini ushlash"),
    "ob_int_goals":     ("goals",     "🎯 Maqsadlarga erishish"),
    "ob_int_learning":  ("learning",  "📚 O'qish / bilim olish"),
    "ob_int_work":      ("work",      "💰 Ish va daromad tartibga solish"),
    "ob_int_discipline":("discipline","🧠 Intizomni oshirish"),
    "ob_int_balance":   ("balance",   "⚖️ Ish va hayotni balanslash"),
}


def get_intent_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Kun tartibini ushlash", callback_data="ob_int_routine")],
        [InlineKeyboardButton(text="🎯 Maqsadlarga erishish", callback_data="ob_int_goals")],
        [InlineKeyboardButton(text="📚 O'qish / bilim olish", callback_data="ob_int_learning")],
        [InlineKeyboardButton(text="💰 Ish va daromad", callback_data="ob_int_work")],
        [InlineKeyboardButton(text="🧠 Intizomni oshirish", callback_data="ob_int_discipline")],
        [InlineKeyboardButton(text="⚖️ Ish-hayot balansi", callback_data="ob_int_balance")],
    ])


@router.callback_query(lambda c: c.data and c.data.startswith("ob_int_"))
async def callback_intent(callback_query: CallbackQuery, user=None) -> None:
    """Step B: Intent selected → go to Step C (Rhythm)."""
    if user is None:
        return

    key = callback_query.data
    if key not in INTENTS:
        return

    intent_value, intent_label = INTENTS[key]

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            db_user.main_intent = intent_value
            db_user.onboarding_step = 2
            await db.commit()

    await callback_query.answer(f"{intent_label} ✓")

    # Step C: Daily Rhythm
    await callback_query.message.edit_text(
        f"✅ {intent_label}\n\n"
        "⏰ <b>Kuningiz ko'proq qanday o'tadi?</b>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🌅 Erta boshlanadi (6-7)", callback_data="ob_rhy_early")],
            [InlineKeyboardButton(text="☀️ O'rtacha tartibda (8-9)", callback_data="ob_rhy_normal")],
            [InlineKeyboardButton(text="🌙 Kechroq ishlayman (10+)", callback_data="ob_rhy_late")],
            [InlineKeyboardButton(text="🔄 Har kuni turlicha", callback_data="ob_rhy_mixed")],
        ]),
    )


# ============================================================
# Step C: Daily Rhythm — "Kuningiz qanday o'tadi?"
# ============================================================

RHYTHMS = {
    "ob_rhy_early":  ("early",  "🌅 Erta boshlash", time(7, 0)),
    "ob_rhy_normal": ("normal", "☀️ O'rtacha", time(8, 0)),
    "ob_rhy_late":   ("late",   "🌙 Kechki", time(10, 0)),
    "ob_rhy_mixed":  ("mixed",  "🔄 Aralash", time(8, 0)),
}


@router.callback_query(lambda c: c.data and c.data.startswith("ob_rhy_"))
async def callback_rhythm(callback_query: CallbackQuery, user=None) -> None:
    """Step C: Rhythm selected → go to Step D (Commitment)."""
    if user is None:
        return

    key = callback_query.data
    if key not in RHYTHMS:
        return

    rhythm_value, rhythm_label, reminder_time = RHYTHMS[key]

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            db_user.daily_rhythm = rhythm_value
            db_user.onboarding_step = 3
            # Auto-set reminder time based on rhythm
            await update_user_settings(db, db_user, UserSettingsUpdate(morning_reminder_time=reminder_time))
            await db.commit()

    await callback_query.answer(f"{rhythm_label} ✓")

    # Step D: Commitment Level
    await callback_query.message.edit_text(
        f"✅ {rhythm_label}\n\n"
        "📊 <b>Boshlanishiga qanchalik reja xohlaysiz?</b>\n\n"
        "<i>Keyin o'zgartirishingiz mumkin</i>",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="🟢 Yengil (2-3 ta task/kun)", callback_data="ob_com_easy")],
            [InlineKeyboardButton(text="🟡 O'rtacha (4-5 ta task/kun)", callback_data="ob_com_medium")],
            [InlineKeyboardButton(text="🔴 Faol rejim (5-7 ta task/kun)", callback_data="ob_com_hard")],
        ]),
    )


# ============================================================
# Step D: Commitment Level — "Qanchalik faol?"
# ============================================================

COMMITMENTS = {
    "ob_com_easy":   ("easy",   "🟢 Yengil"),
    "ob_com_medium": ("medium", "🟡 O'rtacha"),
    "ob_com_hard":   ("hard",   "🔴 Faol"),
}


@router.callback_query(lambda c: c.data and c.data.startswith("ob_com_"))
async def callback_commitment(callback_query: CallbackQuery, user=None) -> None:
    """Step D: Commitment selected → go to Step E (Goal text)."""
    if user is None:
        return

    key = callback_query.data
    if key not in COMMITMENTS:
        return

    com_value, com_label = COMMITMENTS[key]

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if db_user:
            db_user.commitment_level = com_value
            db_user.onboarding_step = 4
            await db.commit()

    await callback_query.answer(f"{com_label} ✓")

    # Step E: Goal text input
    await callback_query.message.edit_text(
        f"✅ {com_label} rejim\n\n"
        "🎯 <b>Asosiy maqsadingiz nima?</b>\n\n"
        "Hozir erishmoqchi bo'lgan eng muhim narsani yozing:\n\n"
        "<i>Masalan:\n"
        "• \"IELTS 7.0 olish\"\n"
        "• \"Freelance loyihalarni ko'paytirish\"\n"
        "• \"Sog'lom turmush tarzi boshlash\"\n"
        "• \"Python o'rganish\"</i>\n\n"
        "👇 Oddiy yozing:",
    )


# ============================================================
# Step E: Goal text — free text input
# ============================================================

@router.message(lambda message: True)
async def handle_onboarding_message(message: Message, user=None) -> None:
    """Catch text during onboarding. Step 4 = goal input."""
    if user is None:
        return

    text = message.text
    if not text or text.startswith("/"):
        return

    # Step E: Goal text (step 4)
    if user.onboarding_step == 4:
        title = text.strip()
        if len(title) < 2:
            await message.answer("Kamida 2 ta belgi yozing. Qayta urinib ko'ring:")
            return
        if len(title) > 200:
            title = title[:200]

        # Create goal
        async with async_session() as db:
            await create_goal(db, user.id, GoalCreate(
                title=title,
                category="personal",
                level="monthly",
            ))
            # Award XP
            await award_xp(db, user.id, "onboarding", None, 15)

            db_user = await get_user_by_id(db, user.id)
            if db_user:
                db_user.onboarding_step = 5
                await db.commit()

        await message.answer(
            f"🎯 Maqsad saqlandi: <b>{title}</b>\n"
            "✨ +15 XP!\n\n"
            "Ajoyib! Oxirgi qadam — tayyor bo'lish 🚀",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="🚀 Boshlash!", callback_data="ob_finish")],
            ]),
        )
        return

    # Old step 1 compatibility (if somehow still at step 1)
    if user.onboarding_step == 1:
        # Redirect to intent selection
        await message.answer(
            "📌 Avval savolga javob bering:",
            reply_markup=get_intent_keyboard(),
        )
        return


# ============================================================
# Step F: Finish — create starter pack + complete
# ============================================================

@router.callback_query(lambda c: c.data == "ob_finish")
async def callback_finish(callback_query: CallbackQuery, user=None) -> None:
    """Final step: create starter pack and finish onboarding."""
    if user is None:
        return

    async with async_session() as db:
        db_user = await get_user_by_id(db, user.id)
        if not db_user:
            return

        # Create starter pack based on 4 signals
        try:
            from app.services.starter_service import create_starter_pack
            await create_starter_pack(
                db, db_user.id,
                segment=db_user.segment or "mixed",
                intent=db_user.main_intent or "routine",
                rhythm=db_user.daily_rhythm or "normal",
                commitment=db_user.commitment_level or "medium",
            )
        except Exception:
            logger.exception("Starter pack creation failed")

        # Activate referral
        try:
            from app.services.referral_service import activate_referral
            await activate_referral(db, db_user.id)
        except Exception:
            pass

        db_user.onboarding_step = 6  # Complete
        await db.commit()

    await callback_query.answer("Tayyor! 🎉")

    from app.config import settings

    keyboard_buttons = []
    mini_app_url = settings.MINI_APP_URL
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
    keyboard_buttons.append([
        InlineKeyboardButton(text="🎯 Maqsadlar", callback_data="cmd_goals_bot"),
    ])

    await callback_query.message.edit_text(
        "🎉 <b>Hammasi tayyor!</b>\n\n"
        "Sizga tayyor reja yaratdim:\n"
        "📋 Bugungi tasklar\n"
        "🔄 Kunlik habitlar\n"
        "🎯 Asosiy maqsad\n"
        "🎯 3 ta kunlik missiya\n\n"
        "Har bir bajarilgan vazifa uchun XP olasiz,\n"
        "streaklar yig'asiz va level oshirasiz! 🚀\n\n"
        "Omad! 💪",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=keyboard_buttons),
    )
