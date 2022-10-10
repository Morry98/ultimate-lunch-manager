import pickle
from typing import Optional

from cachetools.func import ttl_cache
from slack_sdk.web.client import WebClient

from ultimate_lunch_manager.settings import settings_schema, settings_crud


@ttl_cache(maxsize=1, ttl=60)
def get_setting() -> settings_schema.SettingsBase:
    """Get all setting from the database.

    Returns:
        settings_schema.SettingsBase: Setting
    """
    setting_db = settings_crud.get_setting()
    return settings_schema.SettingsBase(
        client=setting_db.client,
        channel_id=setting_db.channel_id,
        channel_name=setting_db.channel_name,
        participants_notification_time=setting_db.participants_notification_time,
        lunch_notification_time=setting_db.lunch_notification_time,
        participants_notification_timezone=setting_db.participants_notification_timezone,
        compute_lunch_timezone=setting_db.compute_lunch_timezone,
    )


@ttl_cache(maxsize=1, ttl=60)
def get_client() -> Optional[WebClient]:
    """Get all setting from the database.

    Returns:
        settings_schema.SettingsBase: Setting
    """
    client = get_setting().client
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
    setting_db = get_setting()
    setting_db.client = pickle.dumps(client)
    return setting_db.client


def update_setting(
    setting: settings_schema.SettingsBase,
) -> settings_schema.SettingsBase:
    """Update setting in the database.

    Args:
        setting (settings_schema.SettingsBase): setting

    Returns:
        settings_schema.SettingsBase: Setting
    """
    setting_db = settings_crud.update_setting(setting=setting)
    return settings_schema.SettingsBase(
        client=setting_db.client,
        channel_id=setting_db.channel_id,
        channel_name=setting_db.channel_name,
        participants_notification_time=setting_db.participants_notification_time,
        lunch_notification_time=setting_db.lunch_notification_time,
        participants_notification_timezone=setting_db.participants_notification_timezone,
        compute_lunch_timezone=setting_db.compute_lunch_timezone,
    )
