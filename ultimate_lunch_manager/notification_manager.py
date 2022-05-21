import random

import datetime
from threading import Thread
from time import sleep
from typing import Optional

TRAINS_EMOJI = [":train2:",
                 ":bullettrain_side:",
                 ":bullettrain_front:",
                 ":light_rail:",
                 ":station:",
                 ":tram:",
                 ":monorail:",]

FOOD_EMOJI = [":poultry_leg:",
              ":hamburger:",
              ":pizza:",
              ":hotdog:",
              ":sandwich:",
              ":taco:",
              ":burrito:",
              ":tamale:",
              ":falafel:",
              ":fried_egg:",
              ":fondue:",
              ":cucumber:",
              ":shallow_pan_of_food:",
              ":spaghetti:",
              ":sushi:",
              ":ramen:",
              ":bento:",
              ":curry:",]

USERS_PARTICIPATING = []
USERS_NOT_PARTICIPATING = []
USER_TIME_PREFERENCES = {}
USER_RESTAURANT_PREFERENCES = {}
PARTICIPANTS_PRIVATE_MESSAGES = {}

def create_participating_message():
    emoji_food = random.choice(FOOD_EMOJI)
    emoji_train = random.choice(TRAINS_EMOJI)
    return [
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"Building up new lunch train {emoji_food}{emoji_train}",
                    "emoji": True
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": "Today are you coming to lunch?"
                }
            },
            {
                "type": "actions",
                "elements": [
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "Sure!",
                            "emoji": True
                        },
                        "style": "primary",
                        "value": "train_participation",
                        "action_id": "confirm_train_participation"
                    },
                    {
                        "type": "button",
                        "text": {
                            "type": "plain_text",
                            "text": "No I hate you!",
                            "emoji": True
                        },
                        "style": "danger",
                        "value": "train_participation",
                        "action_id": "reject_train_participation"
                    }
                ]
            }
        ]


def task(client, channel_name, compute_lunch_datetime, participants_notification_datetime):
    time_diff = participants_notification_datetime - datetime.datetime.utcnow()
    time_diff_seconds = time_diff.total_seconds()
    while time_diff_seconds < 0:
        time_diff_seconds += 24 * 60 * 60  # add 24 hours
    sleep(time_diff_seconds)
    if client is not None and channel_name is not None:
        client.chat_postMessage(
            channel=channel_name,
            text="Building up new lunch train",
            blocks=create_participating_message())


class NotificationManager(Thread):

    def __init__(self, client, channel_name, compute_lunch_datetime, participants_notification_datetime):
        Thread.__init__(self)
        self.t1 = Thread(target=task, args=(client, channel_name, compute_lunch_datetime,
                                            participants_notification_datetime))

    def run(self):
        self.t1.start()


def add_participating_user(user_id, user_name):
    user = {"user_id": user_id, "user_name": user_name}
    USERS_PARTICIPATING.append(user)
    if user in USERS_NOT_PARTICIPATING:
        USERS_NOT_PARTICIPATING.remove(user)


def remove_participating_user(user_id, user_name):
    user = {"user_id": user_id, "user_name": user_name}
    if user in USERS_PARTICIPATING:
        USERS_PARTICIPATING.remove(user)
    USERS_NOT_PARTICIPATING.append(user)


def add_message_to_participants(message_ts, user_id, channel):
    PARTICIPANTS_PRIVATE_MESSAGES[user_id] = (message_ts, channel)


def get_participants_message(user_id):
    return PARTICIPANTS_PRIVATE_MESSAGES[user_id]


def add_user_time_preferences(user_id, time):
    if user_id not in USER_TIME_PREFERENCES:
        USER_TIME_PREFERENCES[user_id] = []
    USER_TIME_PREFERENCES[user_id].append(time)


def remove_user_time_preferences(user_id, time: Optional[str] = None):
    if user_id in USER_TIME_PREFERENCES:
        if time is None:
            USER_TIME_PREFERENCES.pop(user_id)
        elif time in USER_TIME_PREFERENCES[user_id]:
            USER_TIME_PREFERENCES[user_id].remove(time)


def add_user_restaurant_preferences(user_id, restaurant):
    if user_id not in USER_RESTAURANT_PREFERENCES:
        USER_RESTAURANT_PREFERENCES[user_id] = []
    USER_RESTAURANT_PREFERENCES[user_id].append(restaurant)


def remove_user_restaurant_preferences(user_id, restaurant: Optional[str] = None):
    if user_id in USER_RESTAURANT_PREFERENCES:
        if restaurant is None:
            USER_RESTAURANT_PREFERENCES.pop(user_id)
        elif restaurant in USER_RESTAURANT_PREFERENCES[user_id]:
            USER_RESTAURANT_PREFERENCES[user_id].remove(restaurant)
