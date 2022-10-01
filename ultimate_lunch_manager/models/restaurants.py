import datetime

from sqlalchemy import Column, String, Integer, DateTime

from ultimate_lunch_manager.database import Base


class Restaurants(Base):
    __tablename__ = "restaurants"

    id_restaurant = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    priority = Column(Integer, nullable=True)
    creation_date_utc = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
