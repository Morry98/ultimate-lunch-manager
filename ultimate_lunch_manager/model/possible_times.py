import datetime

from sqlalchemy import Column, String, Integer, DateTime

from ultimate_lunch_manager.database import Base


class PossibleTimes(Base):
    __tablename__ = "possible_times"

    id_possible_time = Column(Integer, primary_key=True, index=True)
    time = Column(String, nullable=False)
    priority = Column(Integer, nullable=True)
    creation_date_utc = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
