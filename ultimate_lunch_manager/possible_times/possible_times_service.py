import datetime
from typing import Optional, List, Dict, Any

from cachetools.func import ttl_cache

from ultimate_lunch_manager.possible_times import (
    possible_times_schema,
    possible_times_crud,
)


@ttl_cache(maxsize=128, ttl=60)
def get_possible_times(
    id_possible_time: Optional[int] = None,
    time: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[possible_times_schema.PossibleTimes]:
    """Get possible_times from database.

    Args:
        id_possible_time (Optional[int], optional): id_possible_time. Defaults to None.
        time (Optional[str], optional): time. Defaults to None.
        priority (Optional[int], optional): priority. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.
        skip (int, optional): skip. Defaults to 0.
        limit (int, optional): limit. Defaults to None.

    Returns:
        List[PossibleTimes]: List of possible_times
    """
    possible_times = possible_times_crud.get_possible_times(
        id_possible_time=id_possible_time,
        time=time,
        priority=priority,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
        skip=skip,
        limit=limit,
    )
    return [
        possible_times_schema.PossibleTimes(
            id_possible_time=possible_time.id_possible_time,
            time=possible_time.time,
            priority=possible_time.priority,
            creation_date_utc=possible_time.creation_date_utc,
        )
        for possible_time in possible_times
    ]


def create_possible_time(
    possible_time: possible_times_schema.PossibleTimesBase,
) -> possible_times_schema.PossibleTimes:
    """Create possible_time in database.

    Args:
        possible_time (PossibleTimesBase): possible_time

    Returns:
        PossibleTimes: possible_time
    """
    possible_time = possible_times_crud.create_possible_time(
        possible_time=possible_time,
    )
    return possible_times_schema.PossibleTimes(
        id_possible_time=possible_time.id_possible_time,
        time=possible_time.time,
        priority=possible_time.priority,
        creation_date_utc=possible_time.creation_date_utc,
    )


def update_possible_time(
    id_possible_time: int,
    possible_time: possible_times_schema.PossibleTimesBase,
) -> possible_times_schema.PossibleTimes:
    """Update possible_time in database.

    Args:
        id_possible_time (int): id_possible_time
        possible_time (PossibleTimesBase): possible_time

    Returns:
        PossibleTimes: possible_time
    """
    possible_time = possible_times_crud.update_possible_time(
        id_possible_time=id_possible_time,
        possible_time=possible_time,
    )
    return possible_times_schema.PossibleTimes(
        id_possible_time=possible_time.id_possible_time,
        time=possible_time.time,
        priority=possible_time.priority,
        creation_date_utc=possible_time.creation_date_utc,
    )


def delete_possible_time(
    id_possible_time: Optional[int] = None,
    time: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
) -> int:
    """Delete possible_time from database.

    Args:
        id_possible_time (Optional[int], optional): id_possible_time. Defaults to None.
        time (Optional[str], optional): time. Defaults to None.
        priority (Optional[int], optional): priority. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.

    Returns:
        int: Number of deleted possible_times
    """
    return possible_times_crud.delete_possible_time(
        id_possible_time=id_possible_time,
        time=time,
        priority=priority,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
    )


@ttl_cache(maxsize=1, ttl=60)
def get_time_all_options() -> List[Dict[str, Any]]:
    """Get all possible times.

    Returns:
        List[Dict]: List of possible times
    """
    all_times = get_possible_times()
    all_time_options: List[Dict[str, Any]] = []
    for time in all_times:
        all_time_options.append(
            {
                "text": {
                    "type": "plain_text",
                    "text": time.time,
                    "emoji": True,
                },
                "value": time.time,
            }
        )
    all_time_options = sorted(all_time_options, key=lambda k: k["value"])  # type: ignore
    return all_time_options
