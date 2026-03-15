from pydantic import BaseModel
from app.ai.agents.base import BaseAgent
from app.ai.prompts.motivation import MOTIVATION_SYSTEM_PROMPT
from app.ai.schemas.motivation import MotivationCopy
from app.config import settings


class MotivationCopyAgent(BaseAgent):
    name = "motivation"
    model = settings.AI_MODEL_DEFAULT
    max_tokens = 256

    def get_system_prompt(self) -> str:
        return MOTIVATION_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        parts = []
        parts.append(f"Notification type: {context.get('notification_type', 'morning_reminder')}")
        parts.append(f"User name: {context.get('first_name', 'Foydalanuvchi')}")
        parts.append(f"Streak: {context.get('streak', 0)} days")
        parts.append(f"Tasks today: {context.get('tasks_done', 0)}/{context.get('tasks_total', 0)}")
        parts.append(f"Habits today: {context.get('habits_done', 0)}/{context.get('habits_total', 0)}")
        parts.append(f"Level: {context.get('level', 1)}")

        if context.get("milestone"):
            parts.append(f"Recent milestone: {context['milestone']}")

        parts.append("\nWrite a motivational message. Return JSON.")
        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return MotivationCopy
