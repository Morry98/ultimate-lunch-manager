from sqlalchemy import Column, String, Integer, CLOB

from ultimate_lunch_manager.database import Base


class Settings(Base):
    __tablename__ = "settings"

    id_setting = Column(Integer, primary_key=True, index=True)
    participants_notification_time = Column(String, nullable=True)
    lunch_notification_time = Column(String, nullable=True)
    client = Column(CLOB, nullable=True)
    channel_id = Column(Integer, nullable=True)
    channel_name = Column(String, nullable=True)
    participants_notification_timezone = Column(String, nullable=True)
    compute_lunch_timezone = Column(String, nullable=True)
