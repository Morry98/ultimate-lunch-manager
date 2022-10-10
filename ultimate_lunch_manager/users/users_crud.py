import datetime
from typing import Optional, List

from sqlalchemy.orm import Session

from ultimate_lunch_manager.database import get_db
from ultimate_lunch_manager.users import users_model


def get_users(
    db: Session = next(get_db()),
    id_user: Optional[int] = None,
    slack_user_id: Optional[str] = None,
    is_participating: Optional[bool] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[users_model.Users]:
    """Get users from database.

    Args:
        db (Session): SQLAlchemy
        id_user (Optional[int], optional): id_user. Defaults to None.
        slack_user_id (Optional[str], optional): slack_user_id. Defaults to None.
        is_participating (Optional[bool], optional): is_participating. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.
        skip (int, optional): skip. Defaults to 0.
        limit (int, optional): limit. Defaults to None.

    Returns:
        List[users_model.Users]: List of users
    """
    query = db.query(users_model.Users)
    if id_user is not None:
        query = query.filter(users_model.Users.id_user == id_user)
    if slack_user_id is not None:
        query = query.filter(users_model.Users.slack_user_id == slack_user_id)
    if is_participating is not None:
        query = query.filter(users_model.Users.is_participating == is_participating)
    if start_creation_date_utc is not None:
        query = query.filter(
            users_model.Users.creation_date_utc >= start_creation_date_utc
        )
    if end_creation_date_utc is not None:
        query = query.filter(
            users_model.Users.creation_date_utc <= end_creation_date_utc
        )
    query = query.offset(skip)
    if limit is not None:
        query = query.limit(limit)
    result: List[users_model.Users] = query.all()
    return result


def set_user_participating(
    is_participating: bool,
    slack_user_id: Optional[str] = None,
    db: Session = next(get_db()),
) -> None:
    """Set user as participating.

    Args:
        db (Session): SQLAlchemy
        slack_user_id (str): Slack user id
        is_participating (bool): True if user is participating, False otherwise
    """
    query = db.query(users_model.Users)
    if slack_user_id is not None:
        query = query.filter(users_model.Users.slack_user_id == slack_user_id)
    query.update({users_model.Users.is_participating: is_participating})
    db.commit()
