import os

from pydantic import BaseSettings


class Config(BaseSettings):
    DB_CONN_STR = str(os.getenv("DB_CONN_STR", "postgresql://postgres:postgres@localhost:5432/lunch_manager"))

    SLACK_APP_TOKEN = str(os.getenv("SLACK_APP_TOKEN", "xoxb - 1234"))

    SLACK_TOKEN_SOCKET = str(os.getenv("SLACK_TOKEN_SOCKET", "xapp - 1234"))

    LOG_LEVEL = str(os.getenv("LOG_LEVEL", "INFO"))

    DEV_MESSAGES = str(os.getenv("DEV_MESSAGES", "false")).lower().strip() == "true"
