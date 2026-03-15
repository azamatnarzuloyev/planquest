"""Planner Agent — generates structured daily plans."""

import json

from pydantic import BaseModel

from app.ai.agents.base import BaseAgent
from app.ai.prompts.planner import PLANNER_SYSTEM_PROMPT
from app.ai.schemas.plans import DailyPlan
from app.config import settings


class PlannerAgent(BaseAgent):
    name = "planner"
    model = settings.AI_MODEL_DEFAULT  # gpt-4o-mini

    def get_system_prompt(self) -> str:
        return PLANNER_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        """Build compact context string for the LLM."""
        parts = []

        parts.append(f"Date: {context.get('today_date', '')} ({context.get('day_of_week', '')})")
        parts.append(f"Segment: {context.get('segment', 'other')}")
        parts.append(f"Level: {context.get('current_level', 1)}, Streak: {context.get('streak_current', 0)} kun")
        parts.append(f"Focus today: {context.get('focus_today_minutes', 0)} min")

        # Pending tasks
        pending = context.get("pending_tasks", [])
        if pending:
            parts.append(f"\nPending tasks ({len(pending)}):")
            for t in pending[:15]:
                time_str = f" [{t['estimated_minutes']}m]" if t.get("estimated_minutes") else ""
                parts.append(f"  - {t['title']} | {t['priority']} | {t['difficulty']}{time_str} | id:{t['id']}")
        else:
            parts.append("\nNo pending tasks for today.")

        # Overdue
        overdue = context.get("overdue_tasks", [])
        if overdue:
            parts.append(f"\nOverdue tasks ({len(overdue)}):")
            for t in overdue[:5]:
                parts.append(f"  - {t['title']} | {t['priority']} | from {t['planned_date']} | id:{t['id']}")

        # Habits
        habits = context.get("habits", [])
        if habits:
            done = sum(1 for h in habits if h.get("today_completed"))
            parts.append(f"\nHabits ({done}/{len(habits)} done):")
            for h in habits[:8]:
                status = "✅" if h.get("today_completed") else "⬜"
                parts.append(f"  {status} {h['title']} ({h['type']}) | id:{h['id']}")

        parts.append(f"\nCompleted today: {context.get('completed_today', 0)} tasks")
        parts.append(f"Habits done: {context.get('habits_done_today', 0)}")

        parts.append("\nGenerate a daily plan as JSON.")

        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return DailyPlan
