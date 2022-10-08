from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class SettingsBase(BaseModel):
    participants_notification_time: Optional[datetime] = None
    lunch_notification_time: Optional[datetime] = None
    client: Optional[str] = None
    channel_id: Optional[str] = None
    channel_name: Optional[str] = None
    participants_notification_timezone: Optional[str] = None
    compute_lunch_timezone: Optional[str] = None


class PossibleTimes(SettingsBase):
    id_settings: int

    class Config:
        orm_mode = True
