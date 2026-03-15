from pydantic import BaseModel
from app.ai.agents.base import BaseAgent
from app.ai.prompts.recovery import RECOVERY_SYSTEM_PROMPT
from app.ai.schemas.recovery import RecoveryPlan
from app.config import settings


class RecoveryAgent(BaseAgent):
    name = "recovery"
    model = settings.AI_MODEL_DEFAULT

    def get_system_prompt(self) -> str:
        return RECOVERY_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        parts = []
        parts.append(f"User missed {context.get('missed_days', 1)} days")
        parts.append(f"Today: {context.get('today_date', '')}")
        parts.append(f"Streak before break: {context.get('streak_before', 0)} days")

        overdue = context.get("overdue_tasks", [])
        if overdue:
            parts.append(f"\nOverdue tasks ({len(overdue)}):")
            for t in overdue[:10]:
                parts.append(f"  - {t['title']} | {t['priority']} | from {t['planned_date']} | id:{t['id']}")

        missed_habits = context.get("missed_habits", [])
        if missed_habits:
            parts.append(f"\nMissed habits ({len(missed_habits)}):")
            for h in missed_habits[:5]:
                parts.append(f"  - {h['title']}")

        parts.append(f"\nUser level: {context.get('current_level', 1)}")
        parts.append("\nCreate a recovery plan as JSON.")
        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return RecoveryPlan
