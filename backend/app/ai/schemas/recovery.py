from pydantic import BaseModel, Field


class RescheduleItem(BaseModel):
    task_id: str
    new_date: str


class RecoveryDay(BaseModel):
    focus: str = Field(default="", max_length=100)
    tasks_to_prioritize: list[str] = Field(default_factory=list, max_length=5)
    tasks_to_reschedule: list[RescheduleItem] = Field(default_factory=list, max_length=10)
    tasks_to_archive: list[str] = Field(default_factory=list, max_length=10)
    reduced_habit_target: bool = False


class NextDay(BaseModel):
    date: str = ""
    focus: str = Field(default="", max_length=100)
    return_to_normal: bool = False


class RecoveryPlanData(BaseModel):
    today: RecoveryDay = Field(default_factory=RecoveryDay)
    next_days: list[NextDay] = Field(default_factory=list, max_length=3)


class RecoveryPlan(BaseModel):
    recovery_type: str = Field(default="gentle", pattern=r"^(gentle|moderate|full)$")
    missed_days: int = Field(default=1, ge=1, le=30)
    plan: RecoveryPlanData = Field(default_factory=RecoveryPlanData)
    motivation: str = Field(default="", max_length=200)
