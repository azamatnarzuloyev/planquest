from pydantic import BaseModel, Field


class QuestionOption(BaseModel):
    value: str = Field(..., max_length=40)
    emoji: str = Field(default="📌", max_length=4)


class Question(BaseModel):
    id: str = Field(default="q1", max_length=5)
    text: str = Field(..., max_length=60)
    options: list[QuestionOption] = Field(default_factory=list, min_length=3, max_length=5)


class PlannerQuestions(BaseModel):
    greeting: str = Field(default="", max_length=80)
    questions: list[Question] = Field(default_factory=list, min_length=3, max_length=3)
