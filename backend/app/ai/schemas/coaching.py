from pydantic import BaseModel, Field


class Insight(BaseModel):
    type: str = Field(default="suggestion", pattern=r"^(pattern|warning|achievement|suggestion)$")
    icon: str = Field(default="bulb", pattern=r"^(clock|alert|trophy|bulb|chart|fire)$")
    title: str = Field(..., max_length=80)
    description: str = Field(default="", max_length=200)
    action_suggestion: str | None = None


class CoachingInsights(BaseModel):
    insights: list[Insight] = Field(default_factory=list, min_length=1, max_length=5)
    burnout_risk: str = Field(default="low", pattern=r"^(low|medium|high)$")
    overall_trend: str = Field(default="stable", pattern=r"^(improving|stable|declining)$")
    summary: str = Field(default="", max_length=150)
