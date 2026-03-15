from pydantic import BaseModel, Field


class SuggestedMission(BaseModel):
    title: str = Field(..., max_length=100)
    description: str = Field(default="", max_length=200)
    action: str = Field(..., pattern=r"^(tasks_completed|habits_logged|focus_minutes|focus_sessions)$")
    target_value: int = Field(default=1, ge=1, le=50)
    difficulty: str = Field(default="easy", pattern=r"^(easy|medium|stretch)$")
    reward_xp: int = Field(default=15, ge=10, le=100)
    reward_coins: int = Field(default=5, ge=5, le=50)


class MissionSuggestions(BaseModel):
    suggested_missions: list[SuggestedMission] = Field(default_factory=list, min_length=1, max_length=5)
