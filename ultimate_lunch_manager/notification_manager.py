import random

import datetime
from threading import Thread
from time import sleep

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
    print(f"time diff in seconds: {time_diff.total_seconds()}")
    sleep(time_diff.total_seconds())
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
