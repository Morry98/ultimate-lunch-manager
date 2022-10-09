from sqlalchemy.orm import Session

from ultimate_lunch_manager.database import get_db
from ultimate_lunch_manager.settings import settings_model, settings_schema


def get_settings(
    db: Session = next(get_db()),
) -> settings_model.Settings:
    """Get all settings from the database.

    Args:
        db (Session, optional): Database

    Returns:
        settings_model.Settings: Settings
    """
    result = db.query(settings_model.Settings).first()
    if result is None:
        return create_settings(settings=settings_model.Settings())
    return result  # type: ignore


def update_settings(
    settings: settings_schema.SettingsBase,
    db: Session = next(get_db()),
) -> settings_model.Settings:
    """Update settings in the database.

    Args:
        settings (settings_model.Settings): settings
        db (Session, optional): Database

    Returns:
        settings_model.Settings: Settings
    """
    settings_db = get_settings(db=db)
    settings_db.client = settings.client
    settings_db.channel_id = settings.channel_id
    settings_db.channel_name = settings.channel_name
    settings_db.participants_notification_time = settings.participants_notification_time
    settings_db.lunch_notification_time = settings.lunch_notification_time
    settings_db.participants_notification_timezone = (
        settings.participants_notification_timezone
    )
    settings_db.compute_lunch_timezone = settings.compute_lunch_timezone
    db.commit()
    db.refresh(settings_db)
    return settings_db


def create_settings(
    settings: settings_model.Settings,
    db: Session = next(get_db()),
) -> settings_model.Settings:
    """Create settings in the database, if not exist otherwise update it.

    Args:
        settings (settings_model.Settings): settings
        db (Session, optional): Database

    Returns:
        settings_model.Settings: Settings
    """
    if get_settings() is None:
        db.add(settings)
        db.commit()
        db.refresh(settings)
        return settings
    return update_settings(settings=settings, db=db)
