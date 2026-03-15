from celery import Celery
from celery.schedules import crontab

from app.config import settings

celery_app = Celery(
    "planquest",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
)

# Beat schedule — periodic tasks
celery_app.conf.beat_schedule = {
    "send-morning-reminders": {
        "task": "app.tasks.reminders.send_morning_reminders",
        "schedule": crontab(minute="*/5"),  # every 5 min, checks user timezone
    },
    "send-evening-summaries": {
        "task": "app.tasks.reminders.send_evening_summaries",
        "schedule": crontab(minute="*/5"),
    },
    "send-streak-warnings": {
        "task": "app.tasks.reminders.send_streak_warnings",
        "schedule": crontab(minute="*/10"),
    },
    "reset-daily-message-counts": {
        "task": "app.tasks.reminders.reset_daily_message_counts",
        "schedule": crontab(hour=0, minute=0),  # midnight UTC
    },
    "generate-daily-missions": {
        "task": "app.tasks.reminders.generate_daily_missions",
        "schedule": crontab(hour=0, minute=5),  # 00:05 UTC
    },
    "generate-weekly-missions": {
        "task": "app.tasks.reminders.generate_weekly_missions",
        "schedule": crontab(hour=0, minute=10, day_of_week=1),  # Monday 00:10 UTC
    },
}

# Import tasks explicitly for registration
import app.tasks.reminders  # noqa: F401, E402
