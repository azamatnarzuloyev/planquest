import asyncio
import logging
from datetime import date, datetime, time, timedelta, timezone

from sqlalchemy import and_, select

from app.core.celery_app import celery_app

logger = logging.getLogger(__name__)


def _get_users_for_reminder(reminder_type: str, target_time_field: str):
    """Get users whose local time matches the reminder time (within 5 min window)."""
    import pytz
    from app.core.database import async_session
    from app.models.user import User
    from app.models.user_settings import UserSettings

    async def _fetch():
        now_utc = datetime.now(timezone.utc)
        users_to_notify = []

        async with async_session() as db:
            result = await db.execute(
                select(User, UserSettings)
                .join(UserSettings, UserSettings.user_id == User.id)
                .where(User.is_active == True)
            )
            rows = result.all()

            for user, settings in rows:
                # Check quiet hours
                user_tz = pytz.timezone(user.timezone) if user.timezone != "UTC" else pytz.UTC
                user_now = now_utc.astimezone(user_tz)
                user_time = user_now.time()

                # Quiet hours check
                if _in_quiet_hours(user_time, settings.quiet_hours_start, settings.quiet_hours_end):
                    continue

                # Anti-spam check
                if settings.daily_message_count >= settings.max_daily_messages:
                    continue

                # Check if current user time matches target time (within 5 min)
                target = getattr(settings, target_time_field)
                if _time_in_window(user_time, target, window_minutes=5):
                    users_to_notify.append((user, settings))

        return users_to_notify

    return asyncio.run(_fetch())


def _in_quiet_hours(current: time, start: time, end: time) -> bool:
    """Check if current time is within quiet hours."""
    if start <= end:
        return start <= current <= end
    else:  # overnight quiet hours (e.g., 23:00 - 07:00)
        return current >= start or current <= end


def _time_in_window(current: time, target: time, window_minutes: int = 5) -> bool:
    """Check if current time is within window_minutes of target."""
    current_mins = current.hour * 60 + current.minute
    target_mins = target.hour * 60 + target.minute
    return abs(current_mins - target_mins) <= window_minutes


async def _send_message(telegram_id: int, text: str, reply_markup=None):
    """Send a message via bot."""
    from app.core.bot import bot as bot_instance

    if bot_instance is None:
        logger.warning("Bot not initialized, cannot send message")
        return

    try:
        await bot_instance.send_message(
            chat_id=telegram_id,
            text=text,
            parse_mode="HTML",
            reply_markup=reply_markup,
        )
    except Exception:
        logger.exception(f"Failed to send message to {telegram_id}")


async def _increment_message_count(user_id):
    """Increment daily message count for anti-spam."""
    from app.core.database import async_session
    from app.models.user_settings import UserSettings
    from sqlalchemy import update

    async with async_session() as db:
        await db.execute(
            update(UserSettings)
            .where(UserSettings.user_id == user_id)
            .values(daily_message_count=UserSettings.daily_message_count + 1)
        )
        await db.commit()


# === Morning Reminder ===


@celery_app.task(name="app.tasks.reminders.send_morning_reminders")
def send_morning_reminders():
    """Send morning planning reminders to users whose local time matches."""
    asyncio.run(_send_morning_reminders_async())


async def _send_morning_reminders_async():
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from app.core.database import async_session
    from app.models.user import User
    from app.models.user_settings import UserSettings
    from app.services.task_service import get_tasks
    from app.services.streak_service import get_user_streaks

    users = _get_users_for_reminder("morning", "morning_reminder_time")

    for user, settings in users:
        async with async_session() as db:
            tasks = await get_tasks(db, user.id, planned_date=date.today(), status="pending")
            streaks = await get_user_streaks(db, user.id)

        activity_streak = next((s for s in streaks if s.type == "activity"), None)
        streak_count = activity_streak.current_count if activity_streak else 0

        task_text = ""
        if tasks:
            for i, t in enumerate(tasks[:5], 1):
                task_text += f"  {i}. {t.title}\n"
        else:
            task_text = "  Bugungi reja bo'sh. /add bilan qo'shing!\n"

        text = (
            f"🌅 <b>Xayrli tong, {user.first_name}!</b>\n\n"
            f"🔥 Streak: <b>{streak_count} kun</b>\n\n"
            f"📋 Bugungi vazifalar:\n{task_text}\n"
            f"Yaxshi kun o'tkazing! 💪"
        )

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Bugungi reja", callback_data="cmd_today")],
            [InlineKeyboardButton(text="➕ Task qo'shish", callback_data="cmd_add")],
        ])

        await _send_message(user.telegram_id, text, keyboard)
        await _increment_message_count(user.id)

    logger.info(f"Morning reminders sent to {len(users)} users")


# === Evening Summary ===


@celery_app.task(name="app.tasks.reminders.send_evening_summaries")
def send_evening_summaries():
    """Send evening summary to users whose local time matches."""
    asyncio.run(_send_evening_summaries_async())


async def _send_evening_summaries_async():
    from app.core.database import async_session
    from app.services.task_service import get_tasks
    from app.services.streak_service import get_user_streaks
    from app.services.xp_service import get_or_create_progress
    from app.services.focus_service import get_focus_stats

    users = _get_users_for_reminder("evening", "evening_reminder_time")

    for user, settings in users:
        async with async_session() as db:
            all_tasks = await get_tasks(db, user.id, planned_date=date.today())
            completed = sum(1 for t in all_tasks if t.status == "completed")
            total = len(all_tasks)
            progress = await get_or_create_progress(db, user.id)
            await db.commit()
            focus = await get_focus_stats(db, user.id)
            streaks = await get_user_streaks(db, user.id)

        activity_streak = next((s for s in streaks if s.type == "activity"), None)
        streak_count = activity_streak.current_count if activity_streak else 0
        streak_emoji = "🔥" if streak_count > 0 else "❄️"

        text = (
            f"🌙 <b>Kunlik xulosa, {user.first_name}</b>\n\n"
            f"📋 Vazifalar: <b>{completed}/{total}</b>\n"
            f"⏱ Fokus: <b>{focus['today_minutes']}</b> min\n"
            f"{streak_emoji} Streak: <b>{streak_count} kun</b>\n"
            f"⭐ Level: <b>{progress.current_level}</b>\n\n"
        )

        if completed > 0:
            text += "Ajoyib kun bo'ldi! 🎉"
        elif total > 0:
            text += "Ertaga yanada yaxshiroq bo'ladi! 💪"
        else:
            text += "Ertaga rejalashtirshni boshlang! 📝"

        await _send_message(user.telegram_id, text)
        await _increment_message_count(user.id)

    logger.info(f"Evening summaries sent to {len(users)} users")


# === Streak Warning ===


@celery_app.task(name="app.tasks.reminders.send_streak_warnings")
def send_streak_warnings():
    """Warn users whose streak is at risk (no activity today, evening time)."""
    asyncio.run(_send_streak_warnings_async())


async def _send_streak_warnings_async():
    import pytz
    from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
    from app.core.database import async_session
    from app.models.user import User
    from app.models.user_settings import UserSettings
    from app.services.streak_service import get_user_streaks

    now_utc = datetime.now(timezone.utc)

    async with async_session() as db:
        result = await db.execute(
            select(User, UserSettings)
            .join(UserSettings, UserSettings.user_id == User.id)
            .where(User.is_active == True)
        )
        rows = result.all()

    warned = 0
    for user, settings in rows:
        user_tz = pytz.timezone(user.timezone) if user.timezone != "UTC" else pytz.UTC
        user_now = now_utc.astimezone(user_tz)

        # Only warn between 20:00-21:00
        if not (20 <= user_now.hour <= 20):
            continue

        if _in_quiet_hours(user_now.time(), settings.quiet_hours_start, settings.quiet_hours_end):
            continue
        if settings.daily_message_count >= settings.max_daily_messages:
            continue

        async with async_session() as db:
            streaks = await get_user_streaks(db, user.id)

        activity = next((s for s in streaks if s.type == "activity"), None)
        if activity is None or activity.current_count == 0:
            continue

        # If last_active_date is today, streak is safe
        if activity.last_active_date == date.today():
            continue

        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📋 Bugungi reja", callback_data="cmd_today")],
            [InlineKeyboardButton(text="🔄 Habitlar", callback_data="cmd_habits")],
        ])

        text = (
            f"⚠️ <b>{user.first_name}, streak xavf ostida!</b>\n\n"
            f"🔥 {activity.current_count} kunlik streak'ingiz bugun tugaydi.\n"
            f"Bitta vazifani bajaring yoki habit loglang! 💪"
        )

        await _send_message(user.telegram_id, text, keyboard)
        await _increment_message_count(user.id)
        warned += 1

    logger.info(f"Streak warnings sent to {warned} users")


# === Daily Reset ===


@celery_app.task(name="app.tasks.reminders.reset_daily_message_counts")
def reset_daily_message_counts():
    """Reset daily message counts at midnight UTC."""
    asyncio.run(_reset_counts())


async def _reset_counts():
    from app.core.database import async_session
    from app.models.user_settings import UserSettings
    from sqlalchemy import update

    async with async_session() as db:
        await db.execute(
            update(UserSettings).values(daily_message_count=0)
        )
        await db.commit()

    logger.info("Daily message counts reset")


# === Mission Generation ===


@celery_app.task(name="app.tasks.reminders.generate_daily_missions")
def generate_daily_missions_task():
    """Generate daily missions for all active users at midnight."""
    asyncio.run(_generate_daily_missions_async())


async def _generate_daily_missions_async():
    from app.core.database import async_session
    from app.models.user import User
    from app.services.mission_service import generate_daily_missions, expire_old_missions

    async with async_session() as db:
        # Expire old missions first
        expired = await expire_old_missions(db)
        await db.commit()
        logger.info(f"Expired {expired} old missions")

        # Generate for all active users
        result = await db.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()

    count = 0
    for user in users:
        try:
            async with async_session() as db:
                await generate_daily_missions(db, user.id)
                await db.commit()
                count += 1
        except Exception:
            logger.exception(f"Failed to generate daily missions for user {user.id}")

    logger.info(f"Generated daily missions for {count} users")


@celery_app.task(name="app.tasks.reminders.generate_weekly_missions")
def generate_weekly_missions_task():
    """Generate weekly missions on Monday."""
    asyncio.run(_generate_weekly_missions_async())


async def _generate_weekly_missions_async():
    from app.core.database import async_session
    from app.models.user import User
    from app.services.mission_service import generate_weekly_missions

    async with async_session() as db:
        result = await db.execute(select(User).where(User.is_active == True))
        users = result.scalars().all()

    count = 0
    for user in users:
        try:
            async with async_session() as db:
                await generate_weekly_missions(db, user.id)
                await db.commit()
                count += 1
        except Exception:
            logger.exception(f"Failed to generate weekly missions for user {user.id}")

    logger.info(f"Generated weekly missions for {count} users")
