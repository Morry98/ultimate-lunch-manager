import pickle
from typing import Optional

from cachetools.func import ttl_cache
from slack_sdk.web.client import WebClient

from ultimate_lunch_manager.settings import settings_schema, settings_crud


@ttl_cache(maxsize=1, ttl=60)
def get_settings() -> settings_schema.SettingsBase:
    """Get all settings from the database.

    Returns:
        settings_schema.SettingsBase: Settings
    """
    settings_db = settings_crud.get_settings()
    return settings_schema.SettingsBase(
        client=settings_db.client,
        channel_id=settings_db.channel_id,
        channel_name=settings_db.channel_name,
        participants_notification_time=settings_db.participants_notification_time,
        lunch_notification_time=settings_db.lunch_notification_time,
        participants_notification_timezone=settings_db.participants_notification_timezone,
        compute_lunch_timezone=settings_db.compute_lunch_timezone,
    )


@ttl_cache(maxsize=1, ttl=60)
def get_client() -> Optional[WebClient]:
    """Get all settings from the database.

    Returns:
        settings_schema.SettingsBase: Settings
    """
    client = get_settings().client
    if client is None:
        return None
    return_value: WebClient = pickle.loads(client)
    return return_value


def update_client(client: WebClient) -> bytes:
    """Update client in the database.

    Args:
        client (bytes): client

    Returns:
        bytes: client
    """
    settings_db = get_settings()
    settings_db.client = pickle.dumps(client)
    return settings_db.client


def update_settings(
    settings: settings_schema.SettingsBase,
) -> settings_schema.SettingsBase:
    """Update settings in the database.

    Args:
        settings (settings_schema.SettingsBase): settings

    Returns:
        settings_schema.SettingsBase: Settings
    """
    settings_db = settings_crud.update_settings(settings=settings)
    return settings_schema.SettingsBase(
        client=settings_db.client,
        channel_id=settings_db.channel_id,
        channel_name=settings_db.channel_name,
        participants_notification_time=settings_db.participants_notification_time,
        lunch_notification_time=settings_db.lunch_notification_time,
        participants_notification_timezone=settings_db.participants_notification_timezone,
        compute_lunch_timezone=settings_db.compute_lunch_timezone,
    )
