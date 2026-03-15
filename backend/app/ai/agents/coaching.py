from pydantic import BaseModel
from app.ai.agents.base import BaseAgent
from app.ai.prompts.coaching import COACHING_SYSTEM_PROMPT
from app.ai.schemas.coaching import CoachingInsights
from app.config import settings


class CoachingAgent(BaseAgent):
    name = "coaching"
    model = settings.AI_MODEL_ADVANCED  # gpt-4o — needs deeper analysis

    def get_system_prompt(self) -> str:
        return COACHING_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        parts = []
        parts.append(f"User: {context.get('segment', 'other')} | Level {context.get('current_level', 1)}")
        parts.append(f"Period: last 14 days")

        stats = context.get("analytics", {})
        parts.append(f"\n=== 14-day Stats ===")
        parts.append(f"Avg tasks/day: {stats.get('avg_tasks_per_day', 0):.1f}")
        parts.append(f"Task completion rate: {stats.get('task_completion_rate', 0):.0%}")
        parts.append(f"Avg habits/day: {stats.get('avg_habits_per_day', 0):.1f}")
        parts.append(f"Avg focus min/day: {stats.get('avg_focus_per_day', 0):.0f}")
        parts.append(f"Most productive hour: {stats.get('most_productive_hour', 'unknown')}")
        parts.append(f"Current streak: {stats.get('streak_current', 0)} days")
        parts.append(f"Best streak: {stats.get('streak_best', 0)} days")

        burnout = stats.get("burnout_indicators", {})
        if burnout:
            parts.append(f"\n=== Burnout Indicators ===")
            parts.append(f"Declining completion: {burnout.get('declining_completion', False)}")
            parts.append(f"Reduced focus: {burnout.get('reduced_focus', False)}")
            parts.append(f"Missed habits increasing: {burnout.get('missed_habits_increasing', False)}")

        weekly = context.get("weekly_breakdown", [])
        if weekly:
            parts.append(f"\n=== Weekly Breakdown ===")
            for w in weekly:
                parts.append(f"  {w.get('date', '')}: {w.get('tasks', 0)} tasks, {w.get('habits', 0)} habits")

        parts.append("\nAnalyze patterns and provide coaching insights as JSON.")
        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return CoachingInsights
