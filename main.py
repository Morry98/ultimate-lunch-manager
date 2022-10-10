import datetime
import json
import re
from typing import Optional, List, Any, Dict

import pytz
import requests
from loguru import logger as log
from slack_bolt import App
from slack_bolt.adapter.socket_mode import SocketModeHandler
from slack_sdk.web.client import WebClient

from ultimate_lunch_manager.config.config import Config
from ultimate_lunch_manager.notification_manager import (
    NotificationManager,
    add_message_to_participants,
    get_participants_message,
    add_user_time_preferences,
    remove_user_time_preferences,
    add_user_restaurant_preferences,
    remove_user_restaurant_preferences,
    get_user_info_from_client,
)
from ultimate_lunch_manager.possible_times import (
    possible_times_service,
    possible_times_schema,
)
from ultimate_lunch_manager.restaurants import restaurants_service, restaurants_schema
from ultimate_lunch_manager.settings import settings_service
from ultimate_lunch_manager.users import users_service

config = Config()

log.level(config.LOG_LEVEL)

TIME_VALIDATION = re.compile(r"\d\d:\d\d")

app = App(token=config.SLACK_APP_TOKEN, name="The Ultimate Lunch Manager")

TIME_SELECTED_OPTIONS: List = []
SELECTED_TIME_TO_ADD: Dict = {}  # {user: time}
SELECTED_TIME_TO_DELETE: Dict = {}  # {user: time}
RESTAURANTS_SELECTED_OPTIONS: List = []
SELECTED_RESTAURANT_TO_DELETE: Dict = {}  # {user: restaurant}
NOTIFICATION_DAYS: List = []
NOTIFICATION_DAYS_ALL_OPTIONS: List = [
    {
        "text": {"type": "plain_text", "text": "Monday", "emoji": True},
        "value": "Monday",
    },
    {
        "text": {"type": "plain_text", "text": "Tuesday", "emoji": True},
        "value": "Tuesday",
    },
    {
        "text": {"type": "plain_text", "text": "Wednesday", "emoji": True},
        "value": "Wednesday",
    },
    {
        "text": {"type": "plain_text", "text": "Thursday", "emoji": True},
        "value": "Thursday",
    },
    {
        "text": {"type": "plain_text", "text": "Friday", "emoji": True},
        "value": "Friday",
    },
    {
        "text": {"type": "plain_text", "text": "Saturday", "emoji": True},
        "value": "Saturday",
    },
    {
        "text": {"type": "plain_text", "text": "Sunday", "emoji": True},
        "value": "Sunday",
    },
]
NOTIFICATION_DAYS_SELECTED_OPTIONS: List = []


def create_times_config_message() -> List:
    time_list = "\n- ".join(
        [x.time for x in possible_times_service.get_possible_times()]
    )
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Configurations :gear:",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*These are the times already entered:*{time_list}",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add new time",
                        "emoji": True,
                    },
                    "value": "time_config",
                    "action_id": "add_new_time",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete a time",
                        "emoji": True,
                    },
                    "value": "time_config",
                    "action_id": "delete_time",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Confirm times",
                        "emoji": True,
                    },
                    "style": "primary",
                    "value": "time_config",
                    "action_id": "confirm_times",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Delete all", "emoji": True},
                    "style": "danger",
                    "value": "time_config",
                    "action_id": "delete_all_times",
                },
            ],
        },
    ]


def create_restaurants_config_message() -> List:
    restaurant_list = "\n- ".join(restaurants_service.get_restaurants_names())
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Configurations :gear:",
                "emoji": True,
            },
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": f"*These are the restaurant already entered:*{restaurant_list}",
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Add new restaurant",
                        "emoji": True,
                    },
                    "value": "restaurant_config",
                    "action_id": "add_new_restaurant",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Delete a restaurant",
                        "emoji": True,
                    },
                    "value": "restaurant_config",
                    "action_id": "delete_restaurant",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Confirm restaurants",
                        "emoji": True,
                    },
                    "style": "primary",
                    "value": "restaurant_config",
                    "action_id": "confirm_restaurants",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Delete all", "emoji": True},
                    "style": "danger",
                    "value": "restaurant_config",
                    "action_id": "delete_all_restaurants",
                },
            ],
        },
    ]


def create_notification_days_config_message() -> List:
    if len(NOTIFICATION_DAYS_SELECTED_OPTIONS) > 0:
        checkbox_elements = {
            "type": "checkboxes",
            "options": NOTIFICATION_DAYS_ALL_OPTIONS,
            "initial_options": NOTIFICATION_DAYS_SELECTED_OPTIONS,
            "action_id": "notification_days_selection",
        }
    else:
        checkbox_elements = {
            "type": "checkboxes",
            "options": NOTIFICATION_DAYS_ALL_OPTIONS,
            "action_id": "notification_days_selection",
        }
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Configurations :gear:",
                "emoji": True,
            },
        },
        {
            "type": "input",
            "element": checkbox_elements,
            "label": {
                "type": "plain_text",
                "text": "Select the days when the bot will automatically work",
                "emoji": True,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Select all", "emoji": True},
                    "value": "notification_days",
                    "action_id": "notification_days_select_all",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Unselect all",
                        "emoji": True,
                    },
                    "value": "notification_days",
                    "action_id": "notification_days_unselect_all",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Confirm", "emoji": True},
                    "style": "primary",
                    "value": "notification_days",
                    "action_id": "confirm_notification_days",
                },
            ],
        },
    ]


def create_select_times_message() -> List:
    if len(TIME_SELECTED_OPTIONS) > 0:
        checkbox_elements = {
            "type": "checkboxes",
            "options": possible_times_service.get_time_all_options(),
            "initial_options": TIME_SELECTED_OPTIONS,
            "action_id": "time_selection",
        }
    else:
        checkbox_elements = {
            "type": "checkboxes",
            "options": possible_times_service.get_time_all_options(),
            "action_id": "time_selection",
        }
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Time selection :clock:",
                "emoji": True,
            },
        },
        {
            "type": "input",
            "element": checkbox_elements,
            "label": {
                "type": "plain_text",
                "text": "Select all the times when you are available",
                "emoji": True,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Select all", "emoji": True},
                    "value": "time",
                    "action_id": "time_select_all",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Unselect all",
                        "emoji": True,
                    },
                    "value": "time",
                    "action_id": "time_unselect_all",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Confirm", "emoji": True},
                    "style": "primary",
                    "value": "time",
                    "action_id": "confirm_time_selection",
                },
            ],
        },
    ]


def create_select_restaurant_message() -> List:
    if len(RESTAURANTS_SELECTED_OPTIONS) > 0:
        checkbox_elements = {
            "type": "checkboxes",
            "options": restaurants_service.get_restaurants_all_options(),
            "initial_options": RESTAURANTS_SELECTED_OPTIONS,
            "action_id": "restaurants_selection",
        }
    else:
        checkbox_elements = {
            "type": "checkboxes",
            "options": restaurants_service.get_restaurants_all_options(),
            "action_id": "restaurants_selection",
        }
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Restaurants selection",
                "emoji": True,
            },
        },
        {
            "type": "input",
            "element": checkbox_elements,
            "label": {
                "type": "plain_text",
                "text": "Select all the restaurants you prefer",
                "emoji": True,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Select all", "emoji": True},
                    "value": "restaurants",
                    "action_id": "restaurants_select_all",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Unselect all",
                        "emoji": True,
                    },
                    "value": "restaurants",
                    "action_id": "restaurants_unselect_all",
                },
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Confirm", "emoji": True},
                    "style": "primary",
                    "value": "restaurants",
                    "action_id": "confirm_restaurants_selection",
                },
            ],
        },
    ]


def create_on_board_message() -> List:
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "You are participating to train :sunglasses:",
                "emoji": True,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "See selected preferences!",
                        "emoji": True,
                    },
                    "value": "train_participation",
                    "action_id": "see_preferences",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Update time preferences!",
                        "emoji": True,
                    },
                    "value": "train_participation",
                    "action_id": "update_time_preferences",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Update restaurant preferences!",
                        "emoji": True,
                    },
                    "value": "train_participation",
                    "action_id": "update_restaurant_preferences",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Leave the train!",
                        "emoji": True,
                    },
                    "style": "danger",
                    "value": "train_participation",
                    "action_id": "leave_train",
                },
            ],
        },
    ]


def create_participants_notification_config_message() -> List:
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Configurations :gear:",
                "emoji": True,
            },
        },
        {
            "type": "input",
            "element": {
                "type": "timepicker",
                "initial_time": settings_service.get_setting().participants_notification_time,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select participants notification time",
                    "emoji": True,
                },
                "action_id": "select_participants_notification_time",
            },
            "label": {
                "type": "plain_text",
                "text": "Select participants notification time:",
                "emoji": True,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Confirm", "emoji": True},
                    "style": "primary",
                    "value": "notification_config",
                    "action_id": "confirm_participants_notification_time",
                }
            ],
        },
    ]


def create_compute_lunch_notification_config_message() -> List:
    opt_lunch_notification_time = settings_service.get_setting().lunch_notification_time
    lunch_notification_time: str = (
        opt_lunch_notification_time if opt_lunch_notification_time is not None else ""
    )
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": "Configurations :gear:",
                "emoji": True,
            },
        },
        {
            "type": "input",
            "element": {
                "type": "timepicker",
                "initial_time": lunch_notification_time,
                "placeholder": {
                    "type": "plain_text",
                    "text": "Select computation lunch notification time",
                    "emoji": True,
                },
                "action_id": "select_compute_notification_notification_time",
            },
            "label": {
                "type": "plain_text",
                "text": "Select compute lunch notification time:",
                "emoji": True,
            },
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Confirm", "emoji": True},
                    "style": "primary",
                    "value": "notification_config",
                    "action_id": "confirm_compute_notification_notification_time",
                }
            ],
        },
    ]


@app.command("/start_lunch_manager")
def repeat_text(ack: Any, respond: Any, command: Any) -> None:
    setting = settings_service.get_setting()
    ack()
    if setting.channel_id is None:
        setting.channel_id = command["channel_id"]
        setting.channel_name = command["channel_name"]
        settings_service.update_setting(setting=setting)
        user_name = command["user_name"]
        respond(
            text=f"Bot is started in this channel by {user_name}",
            response_type="in_channel",
        )
        respond(blocks=create_times_config_message(), response_type="ephemeral")
    elif setting.channel_id == command["channel_id"]:
        respond(
            text="Already running in this channel!\nIf you want to stop use /stop",
            response_type="ephemeral",
        )
    else:
        respond(
            text=f"Already running in another channel: {setting.channel_name}\nIf you want to move it use /stop",
            response_type="ephemeral",
        )


@app.action("add_new_time")
def handle_add_new_time(ack: Any, body: Any, client: WebClient) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        default_selected_time = "13:00"
        SELECTED_TIME_TO_ADD[body["user"]["id"]] = default_selected_time
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "Configurations :gear:",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "input",
                            "element": {
                                "type": "timepicker",
                                "initial_time": default_selected_time,
                                "placeholder": {
                                    "type": "plain_text",
                                    "text": "Select time",
                                    "emoji": True,
                                },
                                "action_id": "select_time",
                            },
                            "label": {
                                "type": "plain_text",
                                "text": "Select time:",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Add",
                                        "emoji": True,
                                    },
                                    "style": "primary",
                                    "value": "time_config",
                                    "action_id": "add_selected_time",
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Cancel",
                                        "emoji": True,
                                    },
                                    "style": "danger",
                                    "value": "time_config",
                                    "action_id": "cancel_time_selection",
                                },
                            ],
                        },
                    ],
                }
            ),
        )


@app.action("select_time")
def handle_select_time(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    selected_time = None
    if (
        body is not None
        and "actions" in body
        and "user" in body
        and "id" in body["user"]
    ):
        for action in body["actions"]:
            if (
                "type" in action
                and "selected_time" in action
                and action["type"] == "timepicker"
            ):
                selected_time = action["selected_time"]
                break
        if selected_time is not None:
            SELECTED_TIME_TO_ADD[body["user"]["id"]] = selected_time


@app.action("add_selected_time")
def handle_add_selected_time(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if (
        body is not None
        and "response_url" in body
        and "user" in body
        and "id" in body["user"]
        and body["user"]["id"] in SELECTED_TIME_TO_ADD
    ):
        selected_time = SELECTED_TIME_TO_ADD.pop(body["user"]["id"])
        if selected_time not in [
            x.time for x in possible_times_service.get_possible_times()
        ]:
            possible_times_service.create_possible_time(
                possible_time=possible_times_schema.PossibleTimesBase(
                    time=selected_time,
                )
            )
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_times_config_message(),
                }
            ),
        )


@app.action("cancel_time_selection")
def handle_cancel_time_selection(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:

        if (
            "user" in body
            and "id" in body["user"]
            and body["user"]["id"] in SELECTED_TIME_TO_ADD
        ):
            _ = SELECTED_TIME_TO_ADD.pop(body["user"]["id"])
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_times_config_message(),
                }
            ),
        )


@app.action("delete_time")
def handle_delete_time(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        options = []
        for time in possible_times_service.get_possible_times():
            if time == "":
                continue
            options.append(
                {
                    "text": {"type": "plain_text", "text": time, "emoji": True},
                    "value": time,
                }
            )
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "Configurations :gear:",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Select a time to delete:*",
                            },
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "static_select",
                                    "placeholder": {
                                        "type": "plain_text",
                                        "text": "Select a time",
                                        "emoji": True,
                                    },
                                    "options": options,
                                    "action_id": "select_time_to_delete",
                                }
                            ],
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Confirm",
                                        "emoji": True,
                                    },
                                    "style": "primary",
                                    "value": "time_config",
                                    "action_id": "confirm_time_deletion",
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Cancel",
                                        "emoji": True,
                                    },
                                    "style": "danger",
                                    "value": "time_config",
                                    "action_id": "cancel_time_deletion",
                                },
                            ],
                        },
                    ],
                }
            ),
        )


@app.action("select_time_to_delete")
def handle_select_time_to_delete(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    selected_time = None
    if (
        body is not None
        and "actions" in body
        and "user" in body
        and "id" in body["user"]
    ):
        for action in body["actions"]:
            if (
                "type" in action
                and "selected_option" in action
                and action["type"] == "static_select"
            ):
                if "value" in action["selected_option"]:
                    selected_time = action["selected_option"]["value"]
                break
        if selected_time is not None:
            SELECTED_TIME_TO_DELETE[body["user"]["id"]] = selected_time


@app.action("confirm_time_deletion")
def handle_confirm_time_deletion(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if (
        body is not None
        and "response_url" in body
        and "user" in body
        and "id" in body["user"]
        and body["user"]["id"] in SELECTED_TIME_TO_DELETE
    ):
        selected_time = SELECTED_TIME_TO_DELETE.pop(body["user"]["id"])
        if selected_time in possible_times_service.get_possible_times():
            possible_times_service.delete_possible_time(time=selected_time)
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_times_config_message(),
                }
            ),
        )


@app.action("cancel_time_deletion")
def handle_cancel_time_deletion(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:

        if (
            "user" in body
            and "id" in body["user"]
            and body["user"]["id"] in SELECTED_TIME_TO_DELETE
        ):
            _ = SELECTED_TIME_TO_DELETE.pop(body["user"]["id"])
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_times_config_message(),
                }
            ),
        )


@app.action("confirm_times")
def handle_confirm_times(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        SELECTED_TIME_TO_DELETE.clear()
        SELECTED_TIME_TO_ADD.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_restaurants_config_message(),
                }
            ),
        )


@app.action("delete_all_times")
def handle_delete_all_times(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:

        if (
            "user" in body
            and "id" in body["user"]
            and body["user"]["id"] in SELECTED_TIME_TO_DELETE
        ):
            _ = SELECTED_TIME_TO_DELETE.pop(body["user"]["id"])
        possible_times_service.delete_possible_time()
        SELECTED_TIME_TO_DELETE.clear()
        SELECTED_TIME_TO_ADD.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_times_config_message(),
                }
            ),
        )


@app.action("add_new_restaurant")
def handle_add_new_restaurant(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "Configurations :gear:",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "input",
                            "element": {
                                "type": "plain_text_input",
                                "action_id": "restaurant_name",
                            },
                            "label": {
                                "type": "plain_text",
                                "text": "Insert a restaurant name:",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Confirm",
                                        "emoji": True,
                                    },
                                    "style": "primary",
                                    "value": "time_config",
                                    "action_id": "confirm_restaurant_insertion",
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Cancel",
                                        "emoji": True,
                                    },
                                    "style": "danger",
                                    "value": "time_config",
                                    "action_id": "cancel_restaurant_insertion",
                                },
                            ],
                        },
                    ],
                }
            ),
        )


@app.action("confirm_restaurant_insertion")
def handle_confirm_restaurant_insertion(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if (
        body is not None
        and "state" in body
        and "user" in body
        and "id" in body["user"]
        and "values" in body["state"]
    ):
        for value in body["state"]["values"]:
            for inner_value in body["state"]["values"][value]:
                if "restaurant_name" != inner_value:
                    continue
                temp_inner_value_dict = body["state"]["values"][value][inner_value]
                if "value" in temp_inner_value_dict:
                    selected_restaurant = temp_inner_value_dict["value"]
                    if (
                        selected_restaurant
                        not in restaurants_service.get_restaurants_names()
                    ):
                        restaurants_service.create_restaurant(
                            restaurant=restaurants_schema.RestaurantsBase(
                                name=selected_restaurant
                            )
                        )
                    break

    requests.post(
        url=body["response_url"],
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "replace_original": "true",
                "blocks": create_restaurants_config_message(),
            }
        ),
    )


@app.action("cancel_restaurant_insertion")
def handle_cancel_restaurant_insertion(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        SELECTED_RESTAURANT_TO_DELETE.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_restaurants_config_message(),
                }
            ),
        )


@app.action("delete_restaurant")
def handle_delete_restaurant(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        options = []
        for restaurant in restaurants_service.get_restaurants_names():
            if restaurant == "":
                continue
            options.append(
                {
                    "text": {"type": "plain_text", "text": restaurant, "emoji": True},
                    "value": restaurant,
                }
            )
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": [
                        {
                            "type": "header",
                            "text": {
                                "type": "plain_text",
                                "text": "Configurations :gear:",
                                "emoji": True,
                            },
                        },
                        {
                            "type": "section",
                            "text": {
                                "type": "mrkdwn",
                                "text": "*Select a restaurant to delete:*",
                            },
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "static_select",
                                    "placeholder": {
                                        "type": "plain_text",
                                        "text": "Select a restaurant",
                                        "emoji": True,
                                    },
                                    "options": options,
                                    "action_id": "select_restaurant_to_delete",
                                }
                            ],
                        },
                        {
                            "type": "actions",
                            "elements": [
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Confirm",
                                        "emoji": True,
                                    },
                                    "style": "primary",
                                    "value": "restaurant_config",
                                    "action_id": "confirm_restaurant_deletion",
                                },
                                {
                                    "type": "button",
                                    "text": {
                                        "type": "plain_text",
                                        "text": "Cancel",
                                        "emoji": True,
                                    },
                                    "style": "danger",
                                    "value": "restaurant_config",
                                    "action_id": "cancel_restaurant_deletion",
                                },
                            ],
                        },
                    ],
                }
            ),
        )


@app.action("select_restaurant_to_delete")
def handle_select_restaurant_to_delete(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    selected_restaurant = None
    if (
        body is not None
        and "actions" in body
        and "user" in body
        and "id" in body["user"]
    ):
        for action in body["actions"]:
            if (
                "type" in action
                and "selected_option" in action
                and action["type"] == "static_select"
            ):
                if "value" in action["selected_option"]:
                    selected_restaurant = action["selected_option"]["value"]
                break
        if selected_restaurant is not None:
            SELECTED_RESTAURANT_TO_DELETE[body["user"]["id"]] = selected_restaurant


@app.action("confirm_restaurant_deletion")
def handle_confirm_restaurant_deletion(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if (
        body is not None
        and "response_url" in body
        and "user" in body
        and "id" in body["user"]
        and body["user"]["id"] in SELECTED_RESTAURANT_TO_DELETE
    ):
        selected_restaurant = SELECTED_RESTAURANT_TO_DELETE.pop(body["user"]["id"])
        if selected_restaurant in restaurants_service.get_restaurants_names():
            restaurants_service.delete_restaurants(
                name=selected_restaurant,
            )
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_restaurants_config_message(),
                }
            ),
        )


@app.action("cancel_restaurant_deletion")
def handle_cancel_restaurant_deletion(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:

        if (
            "user" in body
            and "id" in body["user"]
            and body["user"]["id"] in SELECTED_RESTAURANT_TO_DELETE
        ):
            _ = SELECTED_RESTAURANT_TO_DELETE.pop(body["user"]["id"])
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_restaurants_config_message(),
                }
            ),
        )


@app.action("confirm_restaurants")
def handle_confirm_restaurants(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        SELECTED_RESTAURANT_TO_DELETE.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_notification_days_config_message(),
                }
            ),
        )


@app.action("delete_all_restaurants")
def handle_delete_all_restaurants(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:

        if (
            "user" in body
            and "id" in body["user"]
            and body["user"]["id"] in SELECTED_RESTAURANT_TO_DELETE
        ):
            _ = SELECTED_RESTAURANT_TO_DELETE.pop(body["user"]["id"])
        restaurants_service.delete_restaurants()
        restaurants_service.create_restaurant(
            restaurant=restaurants_schema.RestaurantsBase(
                name="",
            )
        )
        SELECTED_RESTAURANT_TO_DELETE.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_restaurants_config_message(),
                }
            ),
        )


@app.action("notification_days_select_all")
def handle_notification_days_select_all(ack: Any, body: Any, client: Any) -> None:
    global NOTIFICATION_DAYS
    global NOTIFICATION_DAYS_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    NOTIFICATION_DAYS = [
        "Monday",
        "Tuesday",
        "Wednesday",
        "Thursday",
        "Friday",
        "Saturday",
        "Sunday",
    ]
    NOTIFICATION_DAYS_SELECTED_OPTIONS = NOTIFICATION_DAYS_ALL_OPTIONS.copy()
    if body is not None and "response_url" in body:
        SELECTED_RESTAURANT_TO_DELETE.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_notification_days_config_message(),
                }
            ),
        )


@app.action("notification_days_unselect_all")
def handle_notification_days_unselect_all(ack: Any, body: Any, client: Any) -> None:
    global NOTIFICATION_DAYS
    global NOTIFICATION_DAYS_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    NOTIFICATION_DAYS = []
    NOTIFICATION_DAYS_SELECTED_OPTIONS = []
    if body is not None and "response_url" in body:
        SELECTED_RESTAURANT_TO_DELETE.clear()
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_notification_days_config_message(),
                }
            ),
        )


@app.action("notification_days_selection")
def handle_notification_days_selection(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "actions" in body:
        for action in body["actions"]:
            if "selected_options" in action:
                NOTIFICATION_DAYS.clear()
                NOTIFICATION_DAYS_SELECTED_OPTIONS.clear()
                for selected_option in action["selected_options"]:
                    day = selected_option["value"]
                    option = {
                        "text": {"type": "plain_text", "text": day, "emoji": True},
                        "value": day,
                    }
                    NOTIFICATION_DAYS.append(day)
                    NOTIFICATION_DAYS_SELECTED_OPTIONS.append(option)


@app.action("confirm_notification_days")
def handle_confirm_notification_days(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_participants_notification_config_message(),
                }
            ),
        )


@app.action("select_participants_notification_time")
def handle_select_participants_notification_time(
    ack: Any, body: Any, client: Any
) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if (
        body is not None
        and "state" in body
        and "user" in body
        and "id" in body["user"]
        and "values" in body["state"]
    ):
        for value in body["state"]["values"]:
            for inner_value in body["state"]["values"][value]:
                if "select_participants_notification_time" != inner_value:
                    continue
                temp_inner_value_dict = body["state"]["values"][value][inner_value]
                if "selected_time" in temp_inner_value_dict:
                    setting = settings_service.get_setting()
                    setting.participants_notification_time = temp_inner_value_dict[
                        "selected_time"
                    ]
                    settings_service.update_setting(setting=setting)
                    break


@app.action("confirm_participants_notification_time")
def handle_confirm_participants_notification_time(
    ack: Any, body: Any, client: Any
) -> None:
    db_client = settings_service.get_client()
    setting = settings_service.get_setting()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    requests.post(
        url=body["response_url"],
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "replace_original": "true",
                "blocks": create_compute_lunch_notification_config_message(),
            }
        ),
    )
    if body is not None and "user" in body and "id" in body["user"]:
        setting.participants_notification_timezone = get_timezone_from_user(
            get_user_info_from_client(client=client, user_id=body["user"]["id"])
        )


@app.action("select_compute_notification_notification_time")
def handle_select_compute_notification_notification_time(
    ack: Any, body: Any, client: Any
) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if (
        body is not None
        and "state" in body
        and "user" in body
        and "id" in body["user"]
        and "values" in body["state"]
    ):
        for value in body["state"]["values"]:
            for inner_value in body["state"]["values"][value]:
                if "select_compute_notification_notification_time" != inner_value:
                    continue
                temp_inner_value_dict = body["state"]["values"][value][inner_value]
                if "selected_time" in temp_inner_value_dict:
                    setting = settings_service.get_setting()
                    setting.lunch_notification_time = temp_inner_value_dict[
                        "selected_time"
                    ]
                    settings_service.update_setting(setting=setting)
                    break


@app.action("confirm_compute_notification_notification_time")
def handle_confirm_compute_notification_notification_time(
    ack: Any, body: Any, client: Any
) -> None:
    db_client = settings_service.get_client()
    setting = settings_service.get_setting()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    requests.post(
        url=body["response_url"],
        headers={"Content-Type": "application/json"},
        data=json.dumps(
            {
                "delete_original": "true",
            }
        ),
    )
    if (
        body is not None
        and "user" in body
        and "name" in body["user"]
        and "id" in body["user"]
    ):
        user_name = body["user"]["name"]
        client.chat_postMessage(
            channel=body["channel"]["id"],
            text=f"Bot has been configured in this channel by {user_name}",
        )
        setting.compute_lunch_timezone = get_timezone_from_user(
            get_user_info_from_client(client=client, user_id=body["user"]["id"])
        )
        settings_service.update_setting(setting=setting)

    notification_manager = NotificationManager(
        client=settings_service.get_client(),
        channel_name=setting.channel_name,
        participants_notification_datetime=convert_time_string_to_utc_datetime(
            time=setting.participants_notification_time,
            timezone=setting.participants_notification_timezone,
        ),
        compute_lunch_datetime=convert_time_string_to_utc_datetime(
            time=settings_service.get_setting().lunch_notification_time,
            timezone=settings_service.get_setting().compute_lunch_timezone,
        ),
        notification_weekdays=NOTIFICATION_DAYS,
    )
    notification_manager.run()


def get_timezone_from_user(user: dict) -> str:
    setting = settings_service.get_setting()
    participants_notification_timezone = (
        setting.participants_notification_timezone
        if setting.participants_notification_timezone is not None
        else "Europe/Amsterdam"
    )
    if user is not None and "tz" in user:
        return str(user["tz"])
    return participants_notification_timezone


def convert_time_string_to_utc_datetime(
    time: Optional[str],
    timezone: Optional[str] = None,
) -> datetime.datetime:
    if timezone is None:
        timezone = "Europe/Amsterdam"
    if time is None:
        time = "11:30"
    if not TIME_VALIDATION.match(time):
        raise ValueError("Invalid time string")
    utc_now = datetime.datetime.utcnow()
    date = utc_now.replace(
        hour=int(time.split(":")[0]),
        minute=int(time.split(":")[1]),
        second=0,
        microsecond=0,
    )
    date = date - datetime.timedelta(
        seconds=get_seconds_difference_from_timezone_name(timezone)
    )
    return date


def get_seconds_difference_from_timezone_name(timezone: str) -> float:
    timezone_offset = datetime.datetime.now(pytz.timezone(timezone)).utcoffset()
    if timezone_offset is None:
        return 0
    return timezone_offset.total_seconds()


@app.action("confirm_train_participation")
def handle_confirm_train_participation(ack: Any, body: Any, client: Any) -> None:
    ack()
    if body is not None and "user" in body and "id" in body["user"]:
        user_info = get_user_info_from_client(client=client, user_id=body["user"]["id"])
        users_service.set_user_participating(
            slack_user_id=user_info["id"], is_participating=True
        )
    client.chat_postEphemeral(
        channel=settings_service.get_setting().channel_name,
        user=body["user"]["id"],
        text="You are participating!",
        blocks=create_select_times_message(),
    )


@app.action("confirm_restaurants_preference")
def handle_confirm_restaurants_preference(ack: Any, body: Any, client: Any) -> None:
    ack()
    if body is not None and "user" in body and "id" in body["user"]:
        user_info = get_user_info_from_client(client=client, user_id=body["user"]["id"])
        users_service.set_user_participating(
            slack_user_id=user_info["id"], is_participating=True
        )
    response = client.chat_postMessage(
        channel=body["user"]["id"],
        user=body["user"]["id"],
        text="You are participating!",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "You are participating to train :sunglasses:",
                    "emoji": True,
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Leave the train!",
                            "emoji": True,
                        },
                        "style": "danger",
                        "value": "train_participation",
                        "action_id": "leave_train",
                    }
                ],
            },
        ],
    )
    if "ok" in response and "ts" in response:
        add_message_to_participants(
            message_ts=response["ts"],
            user_id=body["user"]["id"],
            channel=response["channel"],
        )


@app.action("reject_train_participation")
def handle_reject_train_participation(ack: Any, body: Any, client: Any) -> None:
    ack()
    if body is not None and "user" in body and "id" in body["user"]:
        user_info = get_user_info_from_client(client=client, user_id=body["user"]["id"])
        users_service.set_user_participating(
            slack_user_id=user_info["id"], is_participating=False
        )
    response = client.chat_postMessage(
        channel=body["user"]["id"],
        user=body["user"]["id"],
        text="You are not participating!",
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": "You are not participating to train :smiling_face_with_tear:",
                    "emoji": True,
                },
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Board the train!",
                            "emoji": True,
                        },
                        "style": "primary",
                        "value": "train_participation",
                        "action_id": "board_train",
                    }
                ],
            },
        ],
    )
    if "ok" in response and "ts" in response:
        add_message_to_participants(
            message_ts=response["ts"],
            user_id=body["user"]["id"],
            channel=response["channel"],
        )


@app.action("board_train")
def handle_board_train(ack: Any, body: Any, client: Any) -> None:
    ack()
    if body is not None and "user" in body and "id" in body["user"]:
        user_info = get_user_info_from_client(client=client, user_id=body["user"]["id"])
        users_service.set_user_participating(
            slack_user_id=user_info["id"], is_participating=True
        )
    participants_message = get_participants_message(user_id=body["user"]["id"])
    if participants_message is not None:
        client.chat_update(
            channel=participants_message[1],
            user=body["user"]["id"],
            ts=participants_message[0],
            text="You are participating!",
            blocks=create_on_board_message(),
        )


@app.action("leave_train")
def handle_leave_train(ack: Any, body: Any, client: Any) -> None:
    ack()
    if body is not None and "user" in body and "id" in body["user"]:
        user_info = get_user_info_from_client(client=client, user_id=body["user"]["id"])
        users_service.set_user_participating(
            slack_user_id=user_info["id"], is_participating=False
        )
    participants_message = get_participants_message(user_id=body["user"]["id"])
    if participants_message is not None:
        client.chat_update(
            channel=participants_message[1],
            user=body["user"]["id"],
            ts=participants_message[0],
            text="You are not participating!",
            blocks=[
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "You are not participating to train :smiling_face_with_tear:",
                        "emoji": True,
                    },
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {
                                "type": "plain_text",
                                "text": "Board the train!",
                                "emoji": True,
                            },
                            "style": "primary",
                            "value": "train_participation",
                            "action_id": "board_train",
                        }
                    ],
                },
            ],
        )


@app.action("time_select_all")
def handle_time_select_all(ack: Any, body: Any, client: Any) -> None:
    global TIME_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    for t in possible_times_service.get_possible_times():
        add_user_time_preferences(user_id=body["user"]["id"], time=t)
    TIME_SELECTED_OPTIONS = possible_times_service.get_time_all_options().copy()
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_select_times_message(),
                }
            ),
        )


@app.action("time_unselect_all")
def handle_time_unselect_all(ack: Any, body: Any, client: Any) -> None:
    global TIME_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    TIME_SELECTED_OPTIONS = []
    for t in possible_times_service.get_possible_times():
        remove_user_time_preferences(user_id=body["user"]["id"], time=t.time)
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_select_times_message(),
                }
            ),
        )


@app.action("time_selection")
def handle_time_selection(ack: Any, body: Any, client: Any) -> None:
    global TIME_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "actions" in body:
        for action in body["actions"]:
            if "selected_options" in action:
                remove_user_time_preferences(user_id=body["user"]["id"])
                TIME_SELECTED_OPTIONS.clear()
                for selected_option in action["selected_options"]:
                    t = selected_option["value"]
                    option = {
                        "text": {"type": "plain_text", "text": t, "emoji": True},
                        "value": t,
                    }
                    add_user_time_preferences(user_id=body["user"]["id"], time=t)
                    TIME_SELECTED_OPTIONS.append(option)


@app.action("confirm_time_selection")
def handle_confirm_time(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_select_restaurant_message(),
                }
            ),
        )


@app.action("restaurants_select_all")
def handle_restaurant_select_all(ack: Any, body: Any, client: Any) -> None:
    global RESTAURANTS_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    for r in restaurants_service.get_restaurants_names():
        add_user_restaurant_preferences(user_id=body["user"]["id"], restaurant=r)
    RESTAURANTS_SELECTED_OPTIONS = restaurants_service.get_restaurants_all_options()
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_select_restaurant_message(),
                }
            ),
        )


@app.action("restaurants_unselect_all")
def handle_restaurant_unselect_all(ack: Any, body: Any, client: Any) -> None:
    global RESTAURANTS_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    RESTAURANTS_SELECTED_OPTIONS = []
    for r in restaurants_service.get_restaurants_names():
        remove_user_restaurant_preferences(user_id=body["user"]["id"], restaurant=r)
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "replace_original": "true",
                    "blocks": create_select_restaurant_message(),
                }
            ),
        )


@app.action("restaurants_selection")
def handle_restaurant_selection(ack: Any, body: Any, client: Any) -> None:
    global RESTAURANTS_SELECTED_OPTIONS
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "actions" in body:
        for action in body["actions"]:
            if "selected_options" in action:
                remove_user_restaurant_preferences(user_id=body["user"]["id"])
                RESTAURANTS_SELECTED_OPTIONS.clear()
                for selected_option in action["selected_options"]:
                    r = selected_option["value"]
                    option = {
                        "text": {"type": "plain_text", "text": r, "emoji": True},
                        "value": r,
                    }
                    add_user_restaurant_preferences(
                        user_id=body["user"]["id"], restaurant=r
                    )
                    RESTAURANTS_SELECTED_OPTIONS.append(option)


@app.action("confirm_restaurants_selection")
def handle_confirm_restaurant(ack: Any, body: Any, client: Any) -> None:
    db_client = settings_service.get_client()
    if db_client != client:
        settings_service.update_client(client=client)
    ack()
    if body is not None and "response_url" in body:
        requests.post(
            url=body["response_url"],
            headers={"Content-Type": "application/json"},
            data=json.dumps(
                {
                    "delete_original": "true",
                }
            ),
        )

        response = client.chat_postMessage(
            channel=body["user"]["id"],
            user=body["user"]["id"],
            text="You are participating!",
            blocks=create_on_board_message(),
        )
        if "ok" in response and "ts" in response:
            add_message_to_participants(
                message_ts=response["ts"],
                user_id=body["user"]["id"],
                channel=response["channel"],
            )


@app.event("message")
def handle_message_events(body: Any, logger: Any) -> None:
    pass


def main() -> None:
    handler = SocketModeHandler(app, config.SLACK_TOKEN_SOCKET)
    handler.start()  # type: ignore


if __name__ == "__main__":
    main()
