import datetime as dt
from typing import Optional

from pydantic import BaseModel


class StreakResponse(BaseModel):
    type: str
    current_count: int
    best_count: int
    last_active_date: Optional[dt.date]

    model_config = {"from_attributes": True}
