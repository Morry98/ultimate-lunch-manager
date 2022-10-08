from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class PossibleTimesBase(BaseModel):
    time: str
    priority: Optional[int] = None


class PossibleTimes(PossibleTimesBase):
    id_possible_time: int
    creation_date_utc: Optional[datetime] = None

    class Config:
        orm_mode = True
