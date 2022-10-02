import datetime
from typing import Optional, List

from cachetools.func import ttl_cache

from ultimate_lunch_manager.user import users_schema, users_crud


@ttl_cache(maxsize=128, ttl=60)
def get_users(
    id_user: Optional[int] = None,
    slack_user_id: Optional[str] = None,
    is_participating: Optional[bool] = None,
    start_creation_date_utc: Optional[datetime.datetime] = None,
    end_creation_date_utc: Optional[datetime.datetime] = None,
    skip: int = 0,
    limit: Optional[int] = None,
) -> List[users_schema.Users]:
    """Get users from database.

    Args:
        id_user (Optional[int], optional): id_user. Defaults to None.
        slack_user_id (Optional[str], optional): slack_user_id. Defaults to None.
        is_participating (Optional[bool], optional): is_participating. Defaults to None.
        start_creation_date_utc (Optional[datetime], optional): start_creation_date_utc. Defaults to None.
        end_creation_date_utc (Optional[datetime], optional): end_creation_date_utc. Defaults to None.
        skip (int, optional): skip. Defaults to 0.
        limit (int, optional): limit. Defaults to None.

    Returns:
        List[UsersModel]: List of users
    """
    db_users = users_crud.get_users(
        id_user=id_user,
        slack_user_id=slack_user_id,
        is_participating=is_participating,
        start_creation_date_utc=start_creation_date_utc,
        end_creation_date_utc=end_creation_date_utc,
        skip=skip,
        limit=limit,
    )
    return [
        users_schema.Users(
            id_user=db_user.id_user,
            slack_user_id=db_user.slack_user_id,
            is_participating=db_user.is_participating,
            creation_date_utc=db_user.creation_date_utc,
        )
        for db_user in db_users
    ]


def clear_all_participants() -> None:
    """Clear all participants from database."""
    users_crud.set_user_participating(is_participating=False)


def set_user_participating(
    slack_user_id: str,
    is_participating: bool,
) -> None:
    """Set user as participating.

    Args:
        slack_user_id (str): Slack user id
        is_participating (bool): True if user is participating, False otherwise
    """
    users_crud.set_user_participating(
        slack_user_id=slack_user_id,
        is_participating=is_participating,
    )
