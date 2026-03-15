"""Bot AI commands — /plan, /recover, /coach."""

import logging
from datetime import date

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Message

from app.ai.orchestrator.orchestrator import RateLimitExceeded
from app.ai.services.ai_service import call_agent
from app.ai.tools.analytics import get_analytics_summary, get_recovery_context
from app.ai.tools.context import build_planner_context
from app.ai.schemas.plans import DailyPlan
from app.ai.schemas.recovery import RecoveryPlan
from app.ai.schemas.coaching import CoachingInsights
from app.ai.mappers.plan_mapper import map_suggested_tasks
from app.core.database import async_session
from app.services.task_service import create_task
from app.services.xp_service import get_or_create_progress

logger = logging.getLogger(__name__)

router = Router(name="ai_commands")


@router.message(Command("plan"))
async def cmd_plan(message: Message, user=None) -> None:
    """Generate AI daily plan."""
    if user is None:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return

    if not user.is_premium:
        await message.answer("🔒 AI rejalashtirish faqat Premium foydalanuvchilar uchun.")
        return

    await message.answer("🤖 AI reja tayyorlanmoqda...")

    try:
        async with async_session() as db:
            context = await build_planner_context(db, user.id, user)
            result = await call_agent(
                request_type="daily_plan",
                user_id=user.id,
                context=context,
                db=db,
                cache_key=f"ai:plan:{user.id}:{date.today().isoformat()}",
            )
            await db.commit()

        plan_data = result["data"]
        plan = DailyPlan.model_validate(plan_data)

        # Format plan message
        text = "📋 <b>AI kunlik reja</b>\n\n"

        for block in plan.time_blocks:
            icon = {"task": "📌", "habit": "🔄", "focus_session": "🧠", "break": "☕"}.get(block.type, "📌")
            text += f"{icon} {block.start}-{block.end} — {block.title}\n"

        if plan.suggested_new_tasks:
            text += "\n💡 <b>Yangi tavsiyalar:</b>\n"
            for st in plan.suggested_new_tasks:
                text += f"  • {st.title} ({st.estimated_minutes}m)\n"

        if plan.coaching_note:
            text += f"\n💬 {plan.coaching_note}"

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Qo'llash", callback_data="ai_plan_apply")],
            [InlineKeyboardButton(text="❌ Bekor qilish", callback_data="ai_plan_discard")],
        ])

        await message.answer(text, reply_markup=keyboard)

    except RateLimitExceeded:
        await message.answer("⚠️ Kunlik AI limit tugadi. Ertaga qayta urinib ko'ring.")
    except Exception as e:
        logger.exception("AI plan error in bot")
        await message.answer("❌ AI hozir ishlamayapti. Keyinroq urinib ko'ring.")


@router.callback_query(lambda c: c.data == "ai_plan_apply")
async def cb_plan_apply(callback: CallbackQuery, user=None) -> None:
    """Apply AI plan — create suggested tasks."""
    if user is None:
        await callback.answer("Xatolik")
        return

    # Extract plan from the message (re-generate from cache)
    try:
        async with async_session() as db:
            context = await build_planner_context(db, user.id, user)
            result = await call_agent(
                request_type="daily_plan",
                user_id=user.id,
                context=context,
                db=db,
                cache_key=f"ai:plan:{user.id}:{date.today().isoformat()}",
            )

            plan = DailyPlan.model_validate(result["data"])
            task_creates = map_suggested_tasks(plan, date.today())
            created = 0

            for tc in task_creates:
                tc.source = "ai_plan"
                await create_task(db, user.id, tc)
                created += 1

            await db.commit()

        await callback.message.edit_text(
            callback.message.text + f"\n\n✅ <b>Qo'llanildi!</b> {created} ta task yaratildi.",
        )
        await callback.answer("Reja qo'llanildi!")

    except Exception as e:
        logger.exception("AI plan apply error")
        await callback.answer("Xatolik yuz berdi")


@router.callback_query(lambda c: c.data == "ai_plan_discard")
async def cb_plan_discard(callback: CallbackQuery, user=None) -> None:
    """Discard AI plan."""
    await callback.message.edit_text(
        callback.message.text + "\n\n❌ Bekor qilindi.",
    )
    await callback.answer("Bekor qilindi")


@router.message(Command("recover"))
async def cmd_recover(message: Message, user=None) -> None:
    """Generate recovery plan."""
    if user is None:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return
    if not user.is_premium:
        await message.answer("🔒 AI faqat Premium uchun.")
        return

    await message.answer("🤖 Qaytish rejasi tayyorlanmoqda...")

    try:
        async with async_session() as db:
            context = await get_recovery_context(db, user.id)
            progress = await get_or_create_progress(db, user.id)
            context["current_level"] = progress.current_level

            if context["missed_days"] <= 0:
                await message.answer("✅ Siz hech kun o'tkazib yubormadingiz!")
                return

            result = await call_agent("recovery", user.id, context, db)
            await db.commit()

        data = result["data"]
        plan = data.get("plan", {}).get("today", {})

        text = f"🔄 <b>Qaytish rejasi</b> ({data.get('missed_days', 0)} kun o'tkazildi)\n\n"
        text += f"📌 <b>Bugun:</b> {plan.get('focus', '')}\n"

        if plan.get("tasks_to_prioritize"):
            text += f"⭐ {len(plan['tasks_to_prioritize'])} ta muhim task\n"
        if plan.get("tasks_to_archive"):
            text += f"📦 {len(plan['tasks_to_archive'])} ta arxivlash tavsiya etiladi\n"

        if data.get("motivation"):
            text += f"\n💬 {data['motivation']}"

        await message.answer(text)

    except RateLimitExceeded:
        await message.answer("⚠️ Kunlik AI limit tugadi.")
    except Exception:
        logger.exception("Recovery error")
        await message.answer("❌ AI hozir ishlamayapti.")


@router.message(Command("coach"))
async def cmd_coach(message: Message, user=None) -> None:
    """Get AI coaching insights."""
    if user is None:
        await message.answer("Avval /start buyrug'ini yuboring.")
        return
    if not user.is_premium:
        await message.answer("🔒 AI faqat Premium uchun.")
        return

    await message.answer("🧠 AI tahlil qilmoqda...")

    try:
        async with async_session() as db:
            analytics = await get_analytics_summary(db, user.id, days=14)
            progress = await get_or_create_progress(db, user.id)
            context = {
                "segment": user.segment,
                "current_level": progress.current_level,
                "analytics": analytics,
                "weekly_breakdown": analytics.get("weekly_breakdown", []),
            }

            result = await call_agent("coaching", user.id, context, db)
            await db.commit()

        data = result["data"]
        icon_map = {"clock": "⏰", "alert": "⚠️", "trophy": "🏆", "bulb": "💡", "chart": "📊", "fire": "🔥"}

        text = "🧠 <b>AI Coaching</b>\n\n"

        for insight in data.get("insights", []):
            icon = icon_map.get(insight.get("icon", ""), "💡")
            text += f"{icon} <b>{insight.get('title', '')}</b>\n"
            text += f"   {insight.get('description', '')}\n\n"

        trend = {"improving": "📈 Yaxshilanmoqda", "stable": "➡️ Barqaror", "declining": "📉 Pasaymoqda"}
        text += f"Trend: {trend.get(data.get('overall_trend', ''), '➡️ Barqaror')}\n"

        burnout = data.get("burnout_risk", "low")
        if burnout == "high":
            text += "⚠️ <b>Burnout xavfi yuqori!</b> Dam oling."
        elif burnout == "medium":
            text += "⚡ Burnout xavfi o'rtacha. Ehtiyot bo'ling."

        await message.answer(text)

    except RateLimitExceeded:
        await message.answer("⚠️ Kunlik AI limit tugadi.")
    except Exception:
        logger.exception("Coaching error")
        await message.answer("❌ AI hozir ishlamayapti.")
