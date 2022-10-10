from typing import Optional

from pydantic import BaseModel


class SettingsBase(BaseModel):
    participants_notification_time: Optional[str] = None
    lunch_notification_time: Optional[str] = None
    client: Optional[bytes] = None
    channel_id: Optional[int] = None
    channel_name: Optional[str] = None
    participants_notification_timezone: Optional[str] = None
    compute_lunch_timezone: Optional[str] = None


class Settings(SettingsBase):
    id_setting: int

    class Config:
        orm_mode = True
