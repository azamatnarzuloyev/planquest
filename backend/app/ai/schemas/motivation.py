from pydantic import BaseModel, Field


class MotivationCopy(BaseModel):
    message: str = Field(..., max_length=280)
    tone: str = Field(default="energetic", pattern=r"^(energetic|calm|supportive|celebratory|urgent)$")
    cta_text: str | None = Field(default=None, max_length=20)
    cta_action: str | None = Field(default=None, pattern=r"^(open_planner|open_habits|open_focus|open_progress|null)$")
