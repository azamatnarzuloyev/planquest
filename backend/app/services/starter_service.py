"""Starter pack generator — creates initial tasks, habits, and missions based on 4-layer profiling."""

import logging
from datetime import date
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas.habit import HabitCreate
from app.schemas.task import TaskCreate
from app.services.habit_service import create_habit
from app.services.mission_service import generate_daily_missions
from app.services.task_service import create_task

logger = logging.getLogger(__name__)

# ============================================================
# Task templates per segment × commitment
# ============================================================

STARTER_TASKS = {
    "student": [
        {"title": "📚 Darsga tayyorlanish", "difficulty": "medium", "minutes": 30},
        {"title": "📝 Konspekt yozish", "difficulty": "easy", "minutes": 20},
        {"title": "📖 Kitob o'qish — 20 bet", "difficulty": "easy", "minutes": 30},
        {"title": "✍️ Uy vazifasini bajarish", "difficulty": "medium", "minutes": 45},
        {"title": "🧠 Yangi mavzuni takrorlash", "difficulty": "medium", "minutes": 25},
    ],
    "worker": [
        {"title": "📧 Emaillarni tekshirish", "difficulty": "trivial", "minutes": 15},
        {"title": "💼 Bugungi asosiy vazifa", "difficulty": "medium", "minutes": 60},
        {"title": "📋 Haftalik reja yangilash", "difficulty": "easy", "minutes": 15},
        {"title": "📞 Muhim qo'ng'iroqlar", "difficulty": "easy", "minutes": 20},
        {"title": "📊 Hisobot tayyorlash", "difficulty": "hard", "minutes": 45},
    ],
    "freelancer": [
        {"title": "📧 Client emaillarni javoblash", "difficulty": "easy", "minutes": 15},
        {"title": "💼 Asosiy loyiha ishi", "difficulty": "hard", "minutes": 60},
        {"title": "📋 Haftalik reja tuzish", "difficulty": "easy", "minutes": 15},
        {"title": "💰 Invoice/to'lovlarni tekshirish", "difficulty": "easy", "minutes": 10},
        {"title": "🎨 Portfolio yangilash", "difficulty": "medium", "minutes": 30},
    ],
    "developer": [
        {"title": "💻 Kod yozish — asosiy task", "difficulty": "hard", "minutes": 60},
        {"title": "📖 Documentation o'qish", "difficulty": "easy", "minutes": 30},
        {"title": "🐛 Bug fix / code review", "difficulty": "medium", "minutes": 30},
        {"title": "📚 Tech article o'qish", "difficulty": "easy", "minutes": 15},
        {"title": "🚀 Side project ishlash", "difficulty": "medium", "minutes": 45},
    ],
    "entrepreneur": [
        {"title": "📊 KPI va raqamlarni tekshirish", "difficulty": "easy", "minutes": 15},
        {"title": "🤝 Jamoa bilan meeting", "difficulty": "medium", "minutes": 30},
        {"title": "📈 Strategiya bo'yicha ish", "difficulty": "hard", "minutes": 45},
        {"title": "📞 Hamkorlar bilan aloqa", "difficulty": "easy", "minutes": 20},
        {"title": "💰 Moliyaviy reja yangilash", "difficulty": "medium", "minutes": 30},
    ],
    "homemaker": [
        {"title": "🏠 Uy yig'ishtirish", "difficulty": "easy", "minutes": 30},
        {"title": "🍳 Ovqat tayyorlash rejasi", "difficulty": "easy", "minutes": 15},
        {"title": "🛒 Xarid ro'yxati tuzish", "difficulty": "trivial", "minutes": 10},
        {"title": "👶 Bolalar bilan mashg'ulot", "difficulty": "medium", "minutes": 45},
        {"title": "📚 O'z uchun o'qish", "difficulty": "easy", "minutes": 20},
    ],
    "growth": [
        {"title": "📚 Kitob o'qish — 20 bet", "difficulty": "easy", "minutes": 30},
        {"title": "🧠 Yangi ko'nikma mashq qilish", "difficulty": "medium", "minutes": 45},
        {"title": "✍️ Kundalik yozish", "difficulty": "easy", "minutes": 15},
        {"title": "🎯 Haftalik maqsadlarni ko'rish", "difficulty": "trivial", "minutes": 10},
        {"title": "💪 Sport / jismoniy mashq", "difficulty": "medium", "minutes": 30},
    ],
}
STARTER_TASKS["mixed"] = STARTER_TASKS["growth"]  # Default

# ============================================================
# Habit templates per segment
# ============================================================

STARTER_HABITS = {
    "student": [
        {"title": "Kitob o'qish", "type": "duration", "target_value": 30, "icon": "📚", "frequency": "daily"},
        {"title": "Meditatsiya", "type": "duration", "target_value": 10, "icon": "🧘", "frequency": "daily"},
        {"title": "Kundalik yozish", "type": "yes_no", "target_value": 1, "icon": "✍️", "frequency": "daily"},
    ],
    "worker": [
        {"title": "Suv ichish", "type": "count", "target_value": 8, "icon": "💧", "frequency": "daily"},
        {"title": "Sport", "type": "yes_no", "target_value": 1, "icon": "💪", "frequency": "weekdays"},
        {"title": "Kitob o'qish", "type": "duration", "target_value": 20, "icon": "📚", "frequency": "daily"},
    ],
    "freelancer": [
        {"title": "Inbox zero", "type": "yes_no", "target_value": 1, "icon": "📧", "frequency": "weekdays"},
        {"title": "Sport", "type": "duration", "target_value": 30, "icon": "💪", "frequency": "daily"},
        {"title": "Kitob o'qish", "type": "duration", "target_value": 20, "icon": "📚", "frequency": "daily"},
    ],
    "developer": [
        {"title": "Side project", "type": "duration", "target_value": 30, "icon": "💻", "frequency": "weekdays"},
        {"title": "Tech article", "type": "duration", "target_value": 15, "icon": "📚", "frequency": "weekdays"},
        {"title": "Sport", "type": "yes_no", "target_value": 1, "icon": "💪", "frequency": "daily"},
    ],
    "entrepreneur": [
        {"title": "Yangiliklar o'qish", "type": "duration", "target_value": 10, "icon": "📰", "frequency": "daily"},
        {"title": "Sport", "type": "duration", "target_value": 30, "icon": "💪", "frequency": "daily"},
        {"title": "Kundalik yozish", "type": "yes_no", "target_value": 1, "icon": "📝", "frequency": "daily"},
    ],
    "homemaker": [
        {"title": "Suv ichish", "type": "count", "target_value": 8, "icon": "💧", "frequency": "daily"},
        {"title": "O'z uchun o'qish", "type": "duration", "target_value": 15, "icon": "📚", "frequency": "daily"},
        {"title": "Sport / piyoda yurish", "type": "yes_no", "target_value": 1, "icon": "🚶", "frequency": "daily"},
    ],
    "growth": [
        {"title": "Kitob o'qish", "type": "duration", "target_value": 30, "icon": "📚", "frequency": "daily"},
        {"title": "Meditatsiya", "type": "duration", "target_value": 10, "icon": "🧘", "frequency": "daily"},
        {"title": "Sport", "type": "yes_no", "target_value": 1, "icon": "💪", "frequency": "daily"},
    ],
}
STARTER_HABITS["mixed"] = STARTER_HABITS["growth"]

# ============================================================
# Commitment level → task count
# ============================================================

COMMITMENT_TASK_COUNT = {
    "easy": 2,
    "medium": 3,
    "hard": 5,
}

COMMITMENT_HABIT_COUNT = {
    "easy": 2,
    "medium": 3,
    "hard": 3,
}


async def create_starter_pack(
    db: AsyncSession,
    user_id: UUID,
    segment: str,
    intent: str,
    rhythm: str,
    commitment: str,
) -> dict:
    """Create starter pack: tasks + habits + missions.

    Returns: {tasks_created, habits_created}
    """
    today = date.today()
    task_count = COMMITMENT_TASK_COUNT.get(commitment, 3)
    habit_count = COMMITMENT_HABIT_COUNT.get(commitment, 3)

    # --- Starter Tasks ---
    templates = STARTER_TASKS.get(segment, STARTER_TASKS["mixed"])
    tasks_created = 0

    # Intent-based priority boost
    priority_map = {
        "routine": "medium",
        "goals": "high",
        "learning": "medium",
        "work": "high",
        "discipline": "medium",
        "balance": "low",
    }
    default_priority = priority_map.get(intent, "medium")

    for tmpl in templates[:task_count]:
        await create_task(db, user_id, TaskCreate(
            title=tmpl["title"],
            planned_date=today,
            priority=default_priority,
            difficulty=tmpl["difficulty"],
            estimated_minutes=tmpl["minutes"],
            source="bot",
        ))
        tasks_created += 1

    # --- Starter Habits ---
    habit_templates = STARTER_HABITS.get(segment, STARTER_HABITS["mixed"])
    habits_created = 0

    for tmpl in habit_templates[:habit_count]:
        await create_habit(db, user_id, HabitCreate(
            title=tmpl["title"],
            type=tmpl["type"],
            target_value=tmpl["target_value"],
            icon=tmpl["icon"],
            frequency=tmpl["frequency"],
        ))
        habits_created += 1

    # --- Generate first missions ---
    await generate_daily_missions(db, user_id, today)

    await db.flush()

    logger.info(
        f"Starter pack created: user={user_id} segment={segment} intent={intent} "
        f"rhythm={rhythm} commitment={commitment} "
        f"tasks={tasks_created} habits={habits_created}"
    )

    return {"tasks_created": tasks_created, "habits_created": habits_created}
