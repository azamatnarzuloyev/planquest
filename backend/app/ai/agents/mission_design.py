from pydantic import BaseModel
from app.ai.agents.base import BaseAgent
from app.ai.prompts.mission_design import MISSION_DESIGN_SYSTEM_PROMPT
from app.ai.schemas.missions import MissionSuggestions
from app.config import settings


class MissionDesignAgent(BaseAgent):
    name = "mission_design"
    model = settings.AI_MODEL_DEFAULT

    def get_system_prompt(self) -> str:
        return MISSION_DESIGN_SYSTEM_PROMPT

    def build_user_message(self, context: dict) -> str:
        parts = []
        parts.append(f"User: {context.get('segment', 'other')} | Level {context.get('current_level', 1)}")
        parts.append(f"Streak: {context.get('streak_current', 0)} days")

        stats = context.get("stats", {})
        parts.append(f"\n7-day averages:")
        parts.append(f"  Tasks/day: {stats.get('avg_tasks', 0):.1f}")
        parts.append(f"  Habits/day: {stats.get('avg_habits', 0):.1f}")
        parts.append(f"  Focus min/day: {stats.get('avg_focus', 0):.0f}")
        parts.append(f"  Focus sessions used: {stats.get('focus_used', True)}")

        underused = context.get("underused_features", [])
        if underused:
            parts.append(f"\nUnderutilized: {', '.join(underused)}")

        parts.append("\nDesign 3 personalized daily missions (easy, medium, stretch). Return JSON.")
        return "\n".join(parts)

    def get_output_schema(self) -> type[BaseModel]:
        return MissionSuggestions
