import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from ultimate_lunch_manager.database import get_db
from ultimate_lunch_manager.restaurants import (
    restaurants_model,
    restaurants_schema,
)


def get_restaurants(
    db: Session = next(get_db()),
    id_restaurant: Optional[int] = None,
    name: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[restaurants_model.Restaurants]:
    """Get restaurants from database.

    Args:
        db (Session): SQLAlchemy
        id_restaurant (Optional[int]): id of the restaurant
        name (Optional[str]): name of the restaurant
        priority (Optional[int]): priority of the restaurant
        start_creation_date_utc (Optional[datetime.datetime]): start creation date of the restaurant
        end_creation_date_utc (Optional[datetime.datetime]): end creation date of the restaurant
        skip (int): number of restaurants to skip
        limit (Optional[int]): number of restaurants to return

    Returns:
        List[restaurants_model.PossibleTimes]: List of restaurants
    """
    query = db.query(restaurants_model.Restaurants)
    if id_restaurant is not None:
        query = query.filter(
            restaurants_model.Restaurants.id_restaurant == id_restaurant
        )
    if name is not None:
        query = query.filter(restaurants_model.Restaurants.name == name)
    if priority is not None:
        query = query.filter(restaurants_model.Restaurants.priority == priority)
    if start_creation_date_utc is not None:
        query = query.filter(
            restaurants_model.Restaurants.creation_date_utc >= start_creation_date_utc
        )
    if end_creation_date_utc is not None:
        query = query.filter(
            restaurants_model.Restaurants.creation_date_utc <= end_creation_date_utc
        )
    query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    db_restaurants: List[restaurants_model.Restaurants] = query.all()
    return db_restaurants


def create_restaurant(
    restaurant: restaurants_schema.RestaurantsBase,
    db: Session = next(get_db()),
) -> restaurants_model.Restaurants:
    """Create restaurant in database.

    Args:
        restaurant (restaurants_schema.RestaurantsBase): restaurant
        db (Session): SQLAlchemy

    Returns:
        restaurants_model.Restaurants: restaurant
    """
    db_restaurant = restaurants_model.Restaurants(
        name=restaurant.name,
        priority=restaurant.priority,
    )
    db.add(db_restaurant)
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def update_restaurant(
    id_restaurant: int,
    restaurant: restaurants_schema.RestaurantsBase,
    db: Session = next(get_db()),
) -> restaurants_model.Restaurants:
    """Update restaurant in database.

    Args:
        id_restaurant (int): id of the restaurant
        restaurant (restaurants_schema.RestaurantsBase): restaurant
        db (Session): SQLAlchemy

    Returns:
        restaurants_model.Restaurants: restaurant
    """
    db_restaurant_list = get_restaurants(db=db, id_restaurant=id_restaurant)
    if len(db_restaurant_list) == 0:
        raise ValueError(
            f"Restaurant with id_restaurant={id_restaurant} does not exist"
        )
    elif len(db_restaurant_list) > 1:
        raise ValueError(f"Multiple restaurants with id_restaurant={id_restaurant}")
    db_restaurant = db_restaurant_list[0]
    db_restaurant.name = restaurant.name
    db_restaurant.priority = restaurant.priority
    db.commit()
    db.refresh(db_restaurant)
    return db_restaurant


def delete_restaurants(
    db: Session = next(get_db()),
    id_restaurant: Optional[int] = None,
    name: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
) -> int:
    """Delete restaurants from database.

    Args:
        db (Session): SQLAlchemy
        id_restaurant (Optional[int]): id of the restaurant
        name (Optional[str]): name of the restaurant
        priority (Optional[int]): priority of the restaurant
        start_creation_date_utc (Optional[datetime.datetime]): start creation date of the restaurant
        end_creation_date_utc (Optional[datetime.datetime]): end creation date of the restaurant

    Returns:
        int: number of deleted restaurants
    """
    db_restaurants = get_restaurants(
        db=db,
        id_restaurant=id_restaurant,
        name=name,
        priority=priority,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
    )
    for db_restaurant in db_restaurants:
        db.delete(db_restaurant)
        db.commit()
    return len(db_restaurants)
