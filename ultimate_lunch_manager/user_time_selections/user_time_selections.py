from sqlalchemy import Column, Integer

from ultimate_lunch_manager.database import Base


class UserTimeSelections(Base):
    __tablename__ = "user_time_selections"

    id_user_time_selection = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, nullable=False)
    id_possible_time = Column(Integer, nullable=False)
