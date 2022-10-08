import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from ultimate_lunch_manager.database import get_db
from ultimate_lunch_manager.possible_times import (
    possible_times_model,
    possible_times_schema,
)


def get_possible_times(
    db: Session = next(get_db()),
    id_possible_time: Optional[int] = None,
    time: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[possible_times_model.PossibleTimes]:
    """Get users from database.

    Args:
        db (Session): SQLAlchemy
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
    query = db.query(possible_times_model.PossibleTimes)
    if id_possible_time is not None:
        query = query.filter(
            possible_times_model.PossibleTimes.id_possible_time == id_possible_time
        )
    if time is not None:
        query = query.filter(possible_times_model.PossibleTimes.time == time)
    if priority is not None:
        query = query.filter(possible_times_model.PossibleTimes.priority == priority)
    if start_creation_date_utc is not None:
        query = query.filter(
            possible_times_model.PossibleTimes.creation_date_utc
            >= start_creation_date_utc
        )
    if end_creation_date_utc is not None:
        query = query.filter(
            possible_times_model.PossibleTimes.creation_date_utc
            <= end_creation_date_utc
        )
    if limit is not None:
        query = query.offset(skip).limit(limit)
    # sort query by priority null last
    query = query.order_by(
        possible_times_model.PossibleTimes.priority.desc(nullslast=True)
    )
    result: List[possible_times_model.PossibleTimes] = query.all()
    return result


def create_possible_time(
    possible_time: possible_times_schema.PossibleTimesBase,
    db: Session = next(get_db()),
) -> possible_times_model.PossibleTimes:
    """Create possible_time in database.

    Args:
        db (Session): SQLAlchemy
        possible_time (PossibleTimesBase): possible_time

    Returns:
        PossibleTimes: possible_time
    """
    db_possible_time = possible_times_model.PossibleTimes(
        time=possible_time.time,
        priority=possible_time.priority,
    )
    db.add(db_possible_time)
    db.commit()
    db.refresh(db_possible_time)
    return db_possible_time


def update_possible_time(
    id_possible_time: int,
    possible_time: possible_times_schema.PossibleTimesBase,
    db: Session = next(get_db()),
) -> possible_times_model.PossibleTimes:
    """Update possible_time in database.

    Args:
        id_possible_time (int): id_possible_time
        possible_time (PossibleTimesBase): possible_time
        db (Session): SQLAlchemy

    Returns:
        PossibleTimes: possible_time
    """
    db_possible_times: List[possible_times_model.PossibleTimes] = get_possible_times(
        db, id_possible_time=id_possible_time
    )
    if len(db_possible_times) == 0:
        raise ValueError(
            "No possible_time found with id_possible_time={}".format(id_possible_time)
        )
    elif len(db_possible_times) > 1:
        raise ValueError(
            "Multiple possible_times found with id_possible_time={}".format(
                id_possible_time
            )
        )
    db_possible_time: possible_times_model.PossibleTimes = db_possible_times[0]
    db_possible_time.time = possible_time.time
    db_possible_time.priority = possible_time.priority
    db.commit()
    db.refresh(db_possible_time)
    return db_possible_time


def delete_possible_time(
    db: Session = next(get_db()),
    id_possible_time: Optional[int] = None,
    time: Optional[str] = None,
    priority: Optional[int] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
) -> int:
    """Delete possible_time from database.

    Args:
        db (Session): SQLAlchemy
        id_possible_time (Optional[int], optional): id_possible_time. Defaults to None.
        time (Optional[str], optional): time. Defaults to None.
        priority (Optional[int], optional): priority. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.

    Returns:
        int: Number of deleted possible_times
    """
    db_possible_times = get_possible_times(
        db=db,
        id_possible_time=id_possible_time,
        time=time,
        priority=priority,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
    )
    for db_possible_time in db_possible_times:
        db.delete(db_possible_time)
    db.commit()
    return len(db_possible_times)
