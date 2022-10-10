from typing import Optional

from sqlalchemy.orm import Session

from ultimate_lunch_manager.database import get_db
from ultimate_lunch_manager.settings import settings_model, settings_schema


def get_setting(
    db: Session = next(get_db()),
) -> settings_model.Settings:
    """Get all setting from the database.

    Args:
        db (Session, optional): Database

    Returns:
        settings_model.Settings: Setting
    """
    result: Optional[settings_model.Settings] = db.query(
        settings_model.Settings
    ).first()
    if result is None:
        return create_setting(setting=settings_model.Settings())
    return result


def update_setting(
    setting: settings_schema.SettingsBase,
    db: Session = next(get_db()),
) -> settings_model.Settings:
    """Update setting in the database.

    Args:
        setting (settings_model.Settings): setting
        db (Session, optional): Database

    Returns:
        settings_model.Settings: Setting
    """
    setting_db = get_setting(db=db)
    setting_db.client = setting.client
    setting_db.channel_id = setting.channel_id
    setting_db.channel_name = setting.channel_name
    setting_db.participants_notification_time = setting.participants_notification_time
    setting_db.lunch_notification_time = setting.lunch_notification_time
    setting_db.participants_notification_timezone = (
        setting.participants_notification_timezone
    )
    setting_db.compute_lunch_timezone = setting.compute_lunch_timezone
    db.commit()
    db.refresh(setting_db)
    return setting_db


def create_setting(
    setting: settings_model.Settings,
    db: Session = next(get_db()),
) -> settings_model.Settings:
    """Create setting in the database, if not exist otherwise update it.

    Args:
        setting (settings_model.Settings): setting
        db (Session, optional): Database

    Returns:
        settings_model.Settings: Setting
    """
    if get_setting() is None:
        db.add(setting)
        db.commit()
        db.refresh(setting)
        return setting
    return update_setting(setting=setting, db=db)
