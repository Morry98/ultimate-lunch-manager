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
TIMES = ["", "12:00"]
SELECTED_TIME_TO_ADD = {}  # {user: time}
SELECTED_TIME_TO_DELETE = {}  # {user: time}
RESTAURANTS = ["", "Nonna"]
SELECTED_RESTAURANT_TO_DELETE = {}  # {user: restaurant}


def create_times_config_message():
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
                        "text": "Add new time",
                        "emoji": True
                    },
                    "value": "time_config",
                    "action_id": "add_new_time"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete a time",
                        "emoji": True
                    },
                    "value": "time_config",
                    "action_id": "delete_time"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Confirm times",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": "time_config",
                    "action_id": "confirm_times"
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
                    "action_id": "delete_all_times"
                }
            ]
        }
    ]


def create_restaurant_config_message():
    restaurant_list = "\n- ".join(RESTAURANTS)
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
                "text": f"*These are the restaurant already entered:*{restaurant_list}"
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add new restaurant",
                        "emoji": True
                    },
                    "value": "restaurant_config",
                    "action_id": "add_new_restaurant"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete a restaurant",
                        "emoji": True
                    },
                    "value": "restaurant_config",
                    "action_id": "delete_restaurant"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Confirm restaurants",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": "restaurant_config",
                    "action_id": "confirm_restaurants"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete all",
                        "emoji": True
                    },
                    "style": "danger",
                    "value": "restaurant_config",
                    "action_id": "delete_all_restaurants"
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
        respond(blocks=create_times_config_message(), response_type="ephemeral")
    elif CHANNEL_ID == command["channel_id"]:
        respond(text="Already running in this channel!\nIf you want to stop use /stop", response_type="ephemeral")
    else:
        respond(text=f"Already running in another channel: {CHANNEL_NAME}\nIf you want to move it use /move",
                response_type="ephemeral")


@app.action("add_new_time")
def handle_add_new_time(ack, body, client: WebClient):
    ack()
    if body is not None and "response_url" in body:
        default_selected_time = "13:00"
        SELECTED_TIME_TO_ADD[body["user"]["id"]] = default_selected_time
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
            SELECTED_TIME_TO_ADD[body["user"]["id"]] = selected_time


@app.action("add_selected_time")
def handle_add_selected_time(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body and \
            "user" in body and \
            "id" in body["user"] and \
            body["user"]["id"] in SELECTED_TIME_TO_ADD:
        selected_time = SELECTED_TIME_TO_ADD.pop(body["user"]["id"])
        if selected_time not in TIMES:
            TIMES.append(selected_time)
            TIMES.sort()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_times_config_message(),
            }
            )
        )


@app.action("cancel_time_selection")
def handle_cancel_time_selection(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body:

        if "user" in body and \
                "id" in body["user"] and \
                body["user"]["id"] in SELECTED_TIME_TO_ADD:
            _ = SELECTED_TIME_TO_ADD.pop(body["user"]["id"])
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_times_config_message(),
            }
            )
        )


@app.action("delete_time")
def handle_delete_time(ack, body, client):
    ack()
    if body is not None and "response_url" in body:
        options = []
        for time in TIMES:
            if time == "":
                continue
            options.append({
                "text": {
                    "type": "plain_text",
                    "text": time,
                    "emoji": True
                },
                "value": time
            }
            )
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
                        "type": "section",
                        "text": {
                            "type": "mrkdwn",
                            "text": "*Select a time to delete:*"
                        }
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "static_select",
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select a time",
                                    "emoji": True
                                },
                                "options": options,
                                "action_id": "select_time_to_delete"
                            }
                        ]
                    },
                    {
                        "type": "actions",
                        "elements": [
                            {
                                "type": "button",
                                "text": {
                                    "type": "plain_text",
                                    "text": "Confirm",
                                    "emoji": True
                                },
                                "style": "primary",
                                "value": "time_config",
                                "action_id": "confirm_time_deletion"
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
                                "action_id": "cancel_time_deletion"
                            }
                        ]
                    }
                ]
            }
            )
        )


@app.action("select_time_to_delete")
def handle_select_time_to_delete(ack, body, client):
    ack()
    selected_time = None
    if body is not None and "actions" in body and "user" in body and "id" in body["user"]:
        for action in body["actions"]:
            if "type" in action and "selected_option" in action and action["type"] == "static_select":
                if "value" in action["selected_option"]:
                    selected_time = action["selected_option"]["value"]
                break
        if selected_time is not None:
            SELECTED_TIME_TO_DELETE[body["user"]["id"]] = selected_time


@app.action("confirm_time_deletion")
def handle_confirm_time_deletion(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body and \
            "user" in body and \
            "id" in body["user"] and \
            body["user"]["id"] in SELECTED_TIME_TO_DELETE:
        selected_time = SELECTED_TIME_TO_DELETE.pop(body["user"]["id"])
        if selected_time in TIMES:
            TIMES.remove(selected_time)
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_times_config_message(),
            }
            )
        )


@app.action("cancel_time_deletion")
def handle_cancel_time_deletion(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body:

        if "user" in body and \
                "id" in body["user"] and \
                body["user"]["id"] in SELECTED_TIME_TO_DELETE:
            _ = SELECTED_TIME_TO_DELETE.pop(body["user"]["id"])
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_times_config_message(),
            }
            )
        )


@app.action("confirm_times")
def handle_confirm_times(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body:
        SELECTED_TIME_TO_DELETE.clear()
        SELECTED_TIME_TO_ADD.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_restaurant_config_message(),
            }
            )
        )


@app.action("delete_all_times")
def handle_delete_all_times(ack, body, client):
    global TIMES
    ack()
    if body is not None and \
            "response_url" in body:

        if "user" in body and \
                "id" in body["user"] and \
                body["user"]["id"] in SELECTED_TIME_TO_DELETE:
            _ = SELECTED_TIME_TO_DELETE.pop(body["user"]["id"])
        TIMES.clear()
        TIMES = [""]
        SELECTED_TIME_TO_DELETE.clear()
        SELECTED_TIME_TO_ADD.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_times_config_message(),
            }
            )
        )


@app.action("add_new_restaurant")
def handle_add_new_restaurant(ack, body, client):
    ack()
    if body is not None and "response_url" in body:
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
                            "type": "plain_text_input",
                            "action_id": "restaurant_name"
                        },
                        "label": {
                            "type": "plain_text",
                            "text": "Insert a restaurant name:",
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
                                    "text": "Confirm",
                                    "emoji": True
                                },
                                "style": "primary",
                                "value": "time_config",
                                "action_id": "confirm_restaurant_insertion"
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
                                "action_id": "cancel_restaurant_insertion"
                            }
                        ]
                    }
                ]
            }
            )
        )


@app.action("confirm_restaurant_insertion")
def handle_confirm_restaurant_insertion(ack, body, client):
    ack()
    if body is not None and \
            "state" in body and \
            "user" in body and \
            "id" in body["user"] and \
            "values" in body["state"]:
        for value in body["state"]["values"]:
            for inner_value in body["state"]["values"][value]:
                if "restaurant_name" != inner_value:
                    continue
                temp_inner_value_dict = body["state"]["values"][value][inner_value]
                if "value" in temp_inner_value_dict:
                    selected_restaurant = temp_inner_value_dict["value"]
                    if selected_restaurant not in RESTAURANTS:
                        RESTAURANTS.append(selected_restaurant)
                        RESTAURANTS.sort()
                    break

    requests.post(
        url=body["response_url"],
        headers={"Content-Type": "application/json"},
        data=json.dumps({
            "replace_original": "true",
            "blocks": create_restaurant_config_message(),
        }
        )
    )


@app.action("cancel_restaurant_insertion")
def handle_cancel_restaurant_insertion(ack, body, client):
    ack()
    if body is not None and \
            "response_url" in body:
        SELECTED_RESTAURANT_TO_DELETE.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps({
                "replace_original": "true",
                "blocks": create_restaurant_config_message(),
            }
            )
        )


def main():
    handler = SocketModeHandler(app, SLACK_TOKEN_SOCKET)
    handler.start()


if __name__ == "__main__":
    main()
