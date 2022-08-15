from sqlalchemy import Column, Integer

from ultimate_lunch_manager.database import Base


class UserRestaurantSelections(Base):
    __tablename__ = "user_restaurant_selections"

    id_user_restaurant_selection = Column(Integer, primary_key=True, index=True)
    id_user = Column(Integer, nullable=False)
    id_restaurant = Column(Integer, nullable=False)
