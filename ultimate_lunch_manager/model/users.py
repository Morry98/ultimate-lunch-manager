import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime

from ultimate_lunch_manager.database import Base


class Users(Base):
    __tablename__ = "users"

    id_user = Column(Integer, primary_key=True, index=True)
    slack_user_id = Column(String, nullable=False)
    is_participating = Column(Boolean, nullable=False)
    creation_date_utc = Column(
        DateTime, nullable=False, default=datetime.datetime.utcnow
    )
