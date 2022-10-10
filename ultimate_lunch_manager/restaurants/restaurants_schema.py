from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class RestaurantsBase(BaseModel):
    name: str
    priority: Optional[int] = None


class Restaurants(RestaurantsBase):
    id_restaurant: int
    creation_date_utc: Optional[datetime] = None

    class Config:
        orm_mode = True
