import datetime
import random
from threading import Thread
from time import sleep
from typing import Optional, Dict

TRAINS_EMOJI = [":train2:",
                ":bullettrain_side:",
                ":bullettrain_front:",
                ":light_rail:",
                ":station:",
                ":tram:",
                ":monorail:", ]

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
              ":curry:",
              ":panzerotto:",
              ":eggplant:"]

USERS_PARTICIPATING = []
USERS_NOT_PARTICIPATING = []
USER_TIME_PREFERENCES = {}
USER_RESTAURANT_PREFERENCES = {}
PARTICIPANTS_PRIVATE_MESSAGES = {}
SELECTED_TIME = None
SELECTED_RESTAURANT = None
TIME_DISSATISFIED_USERS = []
RESTAURANT_DISSATISFIED_USERS = []


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


def close_train_message():
    message_text = f"Today the train will start at {SELECTED_TIME} directed to {SELECTED_RESTAURANT}."
    if len(TIME_DISSATISFIED_USERS) > 0:
        message_text += f"\n{TIME_DISSATISFIED_USERS} are not liking the time."
    if len(RESTAURANT_DISSATISFIED_USERS) > 0:
        message_text += f"\n{RESTAURANT_DISSATISFIED_USERS} are not liking the restaurant."
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":warning:The train is closed! Booking needed:warning:",
                "emoji": True
            }
        },
        {
            "type": "section",
            "text": {
                "type": "mrkdwn",
                "text": message_text
            }
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Booking...",
                        "emoji": True
                    },
                    "style": "primary",
                    "value": "train_booking",
                    "action_id": "confirm_train_booking"
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Booking problems",
                        "emoji": True
                    },
                    "style": "danger",
                    "value": "train_booking_problems",
                    "action_id": "confirm_train_booking_problems"
                }
            ]
        }
    ]


class NotificationManager(Thread):

    def __init__(self, client, channel_name, compute_lunch_datetime, participants_notification_datetime):
        Thread.__init__(self)
        self.__client = client
        self.__channel_name = channel_name
        self.__compute_lunch_datetime = compute_lunch_datetime
        self.__participants_notification_datetime = participants_notification_datetime
        self.__selected_time = None
        self.__is_running = False
        self.__train_building_message_ts = None
        self.__train_building_message_channel = None
        self.t1 = Thread(target=self.task)

    def run(self):
        self.__is_running = True
        self.t1.start()

    def stop(self):
        self.__is_running = False
        self.t1.join()

    def is_running(self):
        return self.__is_running

    def get_selected_time(self):
        return self.__selected_time

    def set_selected_time(self, selected_time):
        self.__selected_time = selected_time

    def set_client(self, client):
        self.__client = client

    def set_channel_name(self, channel_name):
        self.__channel_name = channel_name

    def set_compute_lunch_datetime(self, compute_lunch_datetime):
        self.__compute_lunch_datetime = compute_lunch_datetime

    def set_participants_notification_datetime(self, participants_notification_datetime):
        self.__participants_notification_datetime = participants_notification_datetime

    def get_participants_notification_datetime(self):
        return self.__participants_notification_datetime

    def get_compute_lunch_datetime(self):
        return self.__compute_lunch_datetime

    def task(self):
        # move to the next day if the current __participants_notification_datetime is in the past
        time_diff = self.__participants_notification_datetime - datetime.datetime.utcnow()
        time_diff_seconds = time_diff.total_seconds()
        while time_diff_seconds < 0:
            time_diff_seconds += 24 * 60 * 60  # add 24 hours
            self.__participants_notification_datetime += datetime.timedelta(days=1)

        # move to the next day if the current __compute_lunch_datetime is in the past
        time_diff = self.__compute_lunch_datetime - datetime.datetime.utcnow()
        time_diff_seconds = time_diff.total_seconds()
        while time_diff_seconds < 0:
            time_diff_seconds += 24 * 60 * 60  # add 24 hours
            self.__compute_lunch_datetime += datetime.timedelta(days=1)

        # wait until the current __participants_notification_datetime
        # sleep 1 second then check if __participants_notification_datetime is changed or the task is no more running
        time_diff = self.__participants_notification_datetime - datetime.datetime.utcnow()
        time_diff_seconds = time_diff.total_seconds()
        while time_diff_seconds > 0:
            if not self.__is_running:
                return
            if time_diff_seconds < 0:
                break
            sleep(1)
            time_diff = self.__participants_notification_datetime - datetime.datetime.utcnow()
            time_diff_seconds = time_diff.total_seconds()

        # start the train building notification
        if self.__client is not None and self.__channel_name is not None:
            response = self.__client.chat_postMessage(
                channel=self.__channel_name,
                text="Building up new lunch train",
                blocks=create_participating_message())

            if "ok" in response and "ts" in response and "channel" in response:
                self.__train_building_message_ts = response["ts"]
                self.__train_building_message_channel = response["channel"]
            else:
                return None

        # wait until the current __compute_lunch_datetime
        # sleep 1 second then check if __compute_lunch_datetime is changed or the task is no more running
        time_diff = self.__compute_lunch_datetime - datetime.datetime.utcnow()
        time_diff_seconds = time_diff.total_seconds()
        while time_diff_seconds > 0:
            if not self.__is_running:
                return
            if time_diff_seconds < 0:
                break
            sleep(1)
            time_diff = self.__compute_lunch_datetime - datetime.datetime.utcnow()
            time_diff_seconds = time_diff.total_seconds()

        # Closing the train
        if self.__client is not None and self.__channel_name is not None:
            self.__client.chat_delete(
                channel=self.__train_building_message_channel,
                ts=self.__train_building_message_ts
            )
            _compute_selected_parameters(self.__client)
            self.__client.chat_postMessage(
                channel=self.__train_building_message_channel,
                text="Closing lunch train",
                blocks=close_train_message())


def add_participating_user(user_id):
    USERS_PARTICIPATING.append(user_id)
    if user_id in USERS_NOT_PARTICIPATING:
        USERS_NOT_PARTICIPATING.remove(user_id)


def remove_participating_user(user_id):
    if user_id in USERS_PARTICIPATING:
        USERS_PARTICIPATING.remove(user_id)
    USERS_NOT_PARTICIPATING.append(user_id)


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


def _compute_selected_parameters(client) -> None:
    global SELECTED_RESTAURANT
    global SELECTED_TIME
    global TIME_DISSATISFIED_USERS
    global RESTAURANT_DISSATISFIED_USERS

    user_count: int = len(USERS_PARTICIPATING)
    time_preferences_score: Dict[str, int] = {}
    restaurant_preferences_score: Dict[str, int] = {}
    for user, time_preferences in USER_TIME_PREFERENCES.items():
        if user in USERS_NOT_PARTICIPATING:
            continue
        for time in time_preferences:
            if time == "" or time is None:
                continue
            if time not in time_preferences_score:
                time_preferences_score[time] = 0
            time_preferences_score[time] += 1

    for user, restaurant_preferences in USER_RESTAURANT_PREFERENCES.items():
        if user in USERS_NOT_PARTICIPATING:
            continue
        for restaurant in restaurant_preferences:
            if restaurant == "" or restaurant is None:
                continue
            if restaurant not in restaurant_preferences_score:
                restaurant_preferences_score[restaurant] = 0
            restaurant_preferences_score[restaurant] += 1

    if len(time_preferences_score) == 0 or len(restaurant_preferences_score) == 0:
        return

    # sort the time preferences
    time_preference = sorted(time_preferences_score.items(), key=lambda x: x[1], reverse=True)[0]
    restaurant_preference = sorted(restaurant_preferences_score.items(), key=lambda x: x[1], reverse=True)[0]

    time_dissatisfied_users_local = []
    restaurant_dissatisfied_users_local = []
    if int(time_preference[1]) < user_count:
        # find users that hadn't selected the time preference
        for user, time_preferences in USER_TIME_PREFERENCES.items():
            if time_preference[0] not in time_preferences:
                time_dissatisfied_users_local.append(get_user_info_from_client(client, user)["name"])
    if int(restaurant_preference[1]) < user_count:
        # find users that hadn't selected the restaurant preference
        for user, restaurant_preferences in USER_RESTAURANT_PREFERENCES.items():
            if restaurant_preference[0] not in restaurant_preferences:
                restaurant_dissatisfied_users_local.append(get_user_info_from_client(client, user)["name"])

    SELECTED_TIME = time_preference[0]
    SELECTED_RESTAURANT = restaurant_preference[0]
    TIME_DISSATISFIED_USERS = time_dissatisfied_users_local
    RESTAURANT_DISSATISFIED_USERS = restaurant_dissatisfied_users_local
    return


def get_user_info_from_client(client, user_id) -> dict:
    user_info = client.users_info(user=str(user_id))
    if user_info and "ok" in user_info and user_info["ok"] == True and "user" in user_info:
        return user_info["user"]
    return {}
