"""Simple domain event bus — pub/sub within the application."""

import logging
from collections import defaultdict
from typing import Any, Callable, Coroutine

logger = logging.getLogger(__name__)

# Event types
TASK_COMPLETED = "task.completed"
HABIT_LOGGED = "habit.logged"
FOCUS_COMPLETED = "focus.completed"
MISSION_COMPLETED = "mission.completed"
ACHIEVEMENT_UNLOCKED = "achievement.unlocked"
LEVEL_UP = "level.up"
STREAK_MILESTONE = "streak.milestone"

# Registry: event_type → list of async handlers
_handlers: dict[str, list[Callable[..., Coroutine]]] = defaultdict(list)


def on(event_type: str):
    """Decorator to register an event handler."""
    def decorator(func: Callable[..., Coroutine]):
        _handlers[event_type].append(func)
        logger.debug(f"Event handler registered: {event_type} → {func.__name__}")
        return func
    return decorator


async def emit(event_type: str, **kwargs: Any) -> None:
    """Emit a domain event. All registered handlers are called."""
    handlers = _handlers.get(event_type, [])
    if not handlers:
        return

    for handler in handlers:
        try:
            await handler(**kwargs)
        except Exception:
            logger.exception(f"Event handler error: {event_type} → {handler.__name__}")
            # Don't fail the main flow — log and continue


def get_registered_events() -> dict[str, list[str]]:
    """Get all registered events and their handlers (for debugging)."""
    return {k: [h.__name__ for h in v] for k, v in _handlers.items()}
