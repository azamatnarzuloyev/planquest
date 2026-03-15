"""Question Agent — generates personalized pre-planning questions."""

from datetime import date

from pydantic import BaseModel

from app.ai.agents.base import BaseAgent
from app.ai.prompts.questions import QUESTIONS_SYSTEM_PROMPT
from app.ai.schemas.questions import PlannerQuestions
from app.config import settings


class QuestionAgent(BaseAgent):
    name = "questions"
    model = settings.AI_MODEL_DEFAULT
    max_tokens = 512

    def get_system_prompt(self) -> str:
        return QUESTIONS_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        parts = []
        parts.append(f"User: {context.get('first_name', 'Foydalanuvchi')}")
        parts.append(f"Segment: {context.get('segment', 'other')}")
        parts.append(f"Intent: {context.get('main_intent', 'routine')}")
        parts.append(f"Level: {context.get('current_level', 1)}")
        parts.append(f"Streak: {context.get('streak_current', 0)} kun")

        today = date.today()
        parts.append(f"Day: {today.strftime('%A')}")
        parts.append(f"Weekend: {today.weekday() >= 5}")

        # User state signals
        parts.append(f"\nPending tasks today: {context.get('pending_count', 0)}")
        parts.append(f"Overdue tasks: {context.get('overdue_count', 0)}")
        parts.append(f"Habits done today: {context.get('habits_done', 0)}/{context.get('habits_total', 0)}")
        parts.append(f"Missed days: {context.get('missed_days', 0)}")
        parts.append(f"Days since registration: {context.get('days_since_reg', 0)}")
        parts.append(f"Focus today: {context.get('focus_today', 0)} min")

        parts.append("\nGenerate 3 personalized questions as JSON.")
        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return PlannerQuestions
