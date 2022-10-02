from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UsersBase(BaseModel):
    slack_user_id: Optional[str] = None
    is_participating: Optional[bool] = None


class Users(UsersBase):
    id_user: int
    creation_date_utc: Optional[datetime] = None

    class Config:
        orm_mode = True
