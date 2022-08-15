from sqlalchemy import Column, String, Integer

from ultimate_lunch_manager.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id_settings = Column(Integer, primary_key=True, index=True)
    participants_notification_time = Column(String, nullable=False)
    lunch_notification_time = Column(String, nullable=False)
