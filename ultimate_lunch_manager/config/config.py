import os

from pydantic import BaseSettings


class Config(BaseSettings):
    SLACK_APP_TOKEN = str(os.getenv("SLACK_APP_TOKEN", "xoxb - 1234"))

    SLACK_TOKEN_SOCKET = str(os.getenv("SLACK_TOKEN_SOCKET", "xapp - 1234"))

    LOG_LEVEL = str(os.getenv("LOG_LEVEL", "INFO"))
