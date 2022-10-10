import datetime
from typing import Optional, List, Dict, Any

from cachetools.func import ttl_cache

from ultimate_lunch_manager.restaurants import (
    restaurants_schema,
    restaurants_crud,
)


@ttl_cache(maxsize=128, ttl=60)
def get_restaurants(
    id_restaurant: Optional[int] = None,
    name: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[restaurants_schema.Restaurants]:
    """Get restaurants from database.

    Args:
        id_restaurant (Optional[int], optional): id_restaurant. Defaults to None.
        name (Optional[str], optional): name. Defaults to None.
        priority (Optional[int], optional): priority. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.
        skip (int, optional): skip. Defaults to 0.
        limit (Optional[int], optional): limit. Defaults to None.

    Returns:
        List[restaurants_schema.Restaurants]: List of restaurants
    """
    restaurants = restaurants_crud.get_restaurants(
        id_restaurant=id_restaurant,
        name=name,
        priority=priority,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
        skip=skip,
        limit=limit,
    )
    return [
        restaurants_schema.Restaurants(
            id_restaurant=restaurant.id_restaurant,
            name=restaurant.name,
            priority=restaurant.priority,
            creation_date_utc=restaurant.creation_date_utc,
        )
        for restaurant in restaurants
    ]


def create_restaurant(
    restaurant: restaurants_schema.Restaurants,
) -> restaurants_schema.Restaurants:
    """Create restaurants in database.

    Args:
        restaurant (RestaurantsBase): restaurants

    Returns:
        Restaurant: restaurant
    """
    restaurant = restaurants_crud.create_restaurant(
        restaurant=restaurant,
    )
    return restaurants_schema.Restaurants(
        id_restaurant=restaurant.id_restaurant,
        name=restaurant.name,
        priority=restaurant.priority,
        creation_date_utc=restaurant.creation_date_utc,
    )


def update_restaurant(
    id_restaurant: int,
    restaurant: restaurants_schema.Restaurants,
) -> restaurants_schema.Restaurants:
    """Update restaurant in database.

    Args:
        id_restaurant (int): id_restaurant
        restaurant (Restaurants): restaurant

    Returns:
        Restaurants: restaurant
    """
    restaurant = restaurants_crud.update_restaurant(
        id_restaurant=id_restaurant,
        restaurant=restaurant,
    )
    return restaurants_schema.Restaurants(
        id_restaurant=restaurant.id_restaurant,
        name=restaurant.name,
        priority=restaurant.priority,
        creation_date_utc=restaurant.creation_date_utc,
    )


def delete_restaurants(
    id_restaurant: Optional[int] = None,
    name: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
) -> int:
    """Delete restaurants from database.

    Args:
        id_restaurant (List[int]): id_restaurant
        name (Optional[str], optional): name. Defaults to None.
        priority (Optional[int], optional): priority. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.

    Returns:
        int: Number of deleted restaurants
    """
    return restaurants_crud.delete_restaurants(
        id_restaurant=id_restaurant,
        name=name,
        priority=priority,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
    )


@ttl_cache(maxsize=1, ttl=60)
def get_restaurants_all_options() -> List[Dict[str, Any]]:
    """Get all restaurants.

    Returns:
        List[Dict]: List of restaurants
    """
    all_restaurants = get_restaurants()
    all_restaurants_options: List[Dict[str, Any]] = []
    for restaurant in all_restaurants:
        all_restaurants_options.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": restaurant.name,
                    "emoji": True,
                },
                "value": restaurant.name,
            }
        )
    all_restaurants_options = sorted(all_restaurants_options, key=lambda k: k["value"])  # type: ignore
    return all_restaurants_options
