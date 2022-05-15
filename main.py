from loguru import logger as log
import os
import re
import requests
import json

from dotenv import load_dotenv
import pyjokes
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web.client import WebClient

log.level("INFO")

load_dotenv()

SLACK_APP_TOKEN = os.getenv('SLACK_APP_TOKEN')
SLACK_TOKEN_SOCKET = os.getenv('SLACK_TOKEN_SOCKET')

app = App(token=SLACK_APP_TOKEN, name="The Ultimate Lunch Manager")

CHANNEL_ID = None
CHANNEL_NAME = None
POSSIBLE_TIME = []
SELECTED_TIME = {}  # {user: time}
TIMES = ["", "12:00"]


def create_config_message():
    time_list = "\n- ".join(TIMES)
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Configurations :gear:",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*These are the times already entered:*{time_list}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add new value",
                        "emoji": True
                    },
                    "value": "time_config",
                    "action_id": "add_new"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete a value",
                        "emoji": True
                    },
                    "value": "time_config",
                    "action_id": "delete"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete all",
                        "emoji": True
                    },
                    "style": "danger",
                    "value": "time_config",
                    "action_id": "delete_all"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Confirm values",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": "time_config",
                    "action_id": "confirm"
                }
            ]
        }
    ]


@app.message(re.compile(".*"))
def show_random_joke(message, say):
    log.info("Received message: {}".format(message))
    channel_type = message["channel_type"]
    if channel_type != "im":
        log.info(f"{message['user']} tried to use joke command in {message['channel']}")
        return

    dm_channel = message["channel"]
    user_id = message["user"]

    joke = pyjokes.get_joke()

    say(text=joke, channel=dm_channel)


@app.event("message")
def handle_message_events(message, say):
    log.info("Received message: {}".format(message))

    dm_channel = message["channel"]
    user_id = message["user"]

    say(text="Invalid command", channel=dm_channel)


@app.command("/start")
def repeat_text(ack, respond, command):
    global CHANNEL_ID
    global CHANNEL_NAME
    ack()
    if CHANNEL_ID is None:
        CHANNEL_ID = command["channel_id"]
        CHANNEL_NAME = command["channel_name"]
        user_name = command["user_name"]
        respond(text=f"Bot is started in this channel by {user_name}", response_type="in_channel")
        respond(blocks=create_config_message(), response_type="ephemeral")
    elif CHANNEL_ID == command["channel_id"]:
        respond(text="Already running in this channel!\nIf you want to stop use /stop", response_type="ephemeral")
    else:
        respond(text=f"Already running in another channel: {CHANNEL_NAME}\nIf you want to move it use /move",
                response_type="ephemeral")


@app.action("add_new")
def handle_add_new(ack, body, client: WebClient):
    ack()
    if body is not None and "response_url" in body:
        default_selected_time = "13:00"
        SELECTED_TIME[body["user"]["id"]] = default_selected_time
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "Configurations :gear:",
                                "emoji": True
                            }
                        },
                        {
                            "type": "input",
                            "element": {
                                "type": "timepicker",
                                "initial_time": default_selected_time,
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select time",
                                    "emoji": True
                                },
                                "action_id": "select_time"
                            },
                            "label": {
                                "type": "plain_text",
                                "text": "Select time:",
                                "emoji": True
                            }
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Add",
                                        "emoji": True
                                    },
                                    "style": "primary",
                                    "value": "time_config",
                                    "action_id": "add_selected_time"
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Cancel",
                                        "emoji": True
                                    },
                                    "style": "danger",
                                    "value": "time_config",
                                    "action_id": "cancel_time_selection"
                                }
                            ]
                        }
                    ]
            }
            )
        )


@app.action("select_time")
def handle_select_time(ack, body, client):
    ack()
    selected_time = None
    if body is not None and "actions" in body and "user" in body and "id" in body["user"]:
        for action in body["actions"]:
            if "type" in action and "selected_time" in action and action["type"] == "timepicker":
                selected_time = action["selected_time"]
                break
        if selected_time is not None:
            SELECTED_TIME[body["user"]["id"]] = selected_time


@app.action("add_selected_time")
def handle_add_selected_time(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body and \
            "user" in body and \
            "id" in body["user"] and \
            body["user"]["id"] in SELECTED_TIME:
        selected_time = SELECTED_TIME.pop(body["user"]["id"])
        if selected_time not in TIMES:
            TIMES.append(selected_time)
            TIMES.sort()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_config_message(),
            }
            )
        )


def main():
    handler = SocketModeHandler(app, SLACK_TOKEN_SOCKET)
    handler.start()


if __name__ == "__main__":
    main()
