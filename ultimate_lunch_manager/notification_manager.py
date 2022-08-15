import datetime
import random
from threading import Thread
from time import sleep
from typing import Optional, Dict, List, Tuple, Any

import loguru
import pyjokes

from ultimate_lunch_manager.config.config import Config

config = Config()

TRAINS_EMOJI: List = [
    ":train2:",
    ":bullettrain_side:",
    ":bullettrain_front:",
    ":light_rail:",
    ":station:",
    ":tram:",
    ":monorail:",
]

FOOD_EMOJI: Any = [
    ":poultry_leg:",
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
    ":eggplant:",
]

WEEKDAY_NUMBER_TO_STRING: Dict[int, str] = {
    0: "monday",
    1: "tuesday",
    2: "wednesday",
    3: "thursday",
    4: "friday",
    5: "saturday",
    6: "sunday",
}

USERS_PARTICIPATING: Any = []
USERS_NOT_PARTICIPATING: Any = []
USER_TIME_PREFERENCES: Any = {}
USER_RESTAURANT_PREFERENCES: Any = {}
PARTICIPANTS_PRIVATE_MESSAGES: Any = {}
SELECTED_TIME: Any = None
SELECTED_RESTAURANT: Any = None
TIME_DISSATISFIED_USERS: Any = []
RESTAURANT_DISSATISFIED_USERS: Any = []


def create_participating_message() -> List:
    emoji_food = random.choice(FOOD_EMOJI)
    emoji_train = random.choice(TRAINS_EMOJI)
    rand_int = random.randint(0, 100)
    if rand_int < 5:
        joke = pyjokes.get_joke(category="chuck")
    elif rand_int < 40:
        joke = pyjokes.get_joke(language="it")
    else:
        joke = pyjokes.get_joke()
    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": f"Building up new lunch train {emoji_food}{emoji_train}",
                "emoji": True,
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": joke}},
        {
            "type": "section",
            "text": {"type": "mrkdwn", "text": "Today are you coming to lunch?"},
        },
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Sure!", "emoji": True},
                    "style": "primary",
                    "value": "train_participation",
                    "action_id": "confirm_train_participation",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "No I hate you!",
                        "emoji": True,
                    },
                    "style": "danger",
                    "value": "train_participation",
                    "action_id": "reject_train_participation",
                },
            ],
        },
    ]


def close_train_message(client: Any) -> List:
    message_text = f"Today the train will start at {SELECTED_TIME} directed to {SELECTED_RESTAURANT}."
    if len(TIME_DISSATISFIED_USERS) > 0:
        message_text += f"\n{TIME_DISSATISFIED_USERS} are not liking the time."
    if len(RESTAURANT_DISSATISFIED_USERS) > 0:
        message_text += (
            f"\n{RESTAURANT_DISSATISFIED_USERS} are not liking the restaurant."
        )
    if config.DEV_MESSAGES:
        message_text += "\n\n\n"
        debug_participating_message = "user participating:\n"
        debug_time_pref_message = "\nuser time preferences:\n"
        debug_rest_pref_message = "\nuser restaurant preferences:\n"
        for u in USERS_PARTICIPATING:
            user_name = get_user_info_from_client(client, u)["name"]
            debug_participating_message += f"- {user_name}\n"
            debug_time_pref_message += (
                f"- {user_name}: "
                f"{[x for x in USER_TIME_PREFERENCES[u] if x != '' and x is not None]}\n"
            )
            debug_rest_pref_message += (
                f"- {user_name}: "
                f"{[x for x in USER_RESTAURANT_PREFERENCES[u] if x != '' and x is not None]}\n"
            )

        message_text += (
            debug_participating_message
            + "\n"
            + debug_time_pref_message
            + "\n"
            + debug_rest_pref_message
        )

    return [
        {
            "type": "header",
            "text": {
                "type": "plain_text",
                "text": ":warning:The train is closed! Booking needed:warning:",
                "emoji": True,
            },
        },
        {"type": "section", "text": {"type": "mrkdwn", "text": message_text}},
        {
            "type": "actions",
            "elements": [
                {
                    "type": "button",
                    "text": {"type": "plain_text", "text": "Booking...", "emoji": True},
                    "style": "primary",
                    "value": "train_booking",
                    "action_id": "confirm_train_booking",
                },
                {
                    "type": "button",
                    "text": {
                        "type": "plain_text",
                        "text": "Booking problems",
                        "emoji": True,
                    },
                    "style": "danger",
                    "value": "train_booking_problems",
                    "action_id": "confirm_train_booking_problems",
                },
            ],
        },
    ]


class NotificationManager(Thread):
    def __init__(
        self,
        client: Any,
        channel_name: Any,
        compute_lunch_datetime: Any,
        participants_notification_datetime: Any,
        notification_weekdays: Any,
    ) -> None:
        Thread.__init__(self)
        self.__client = client
        self.__channel_name = channel_name
        self.__compute_lunch_datetime = compute_lunch_datetime
        self.__participants_notification_datetime = participants_notification_datetime
        self.__selected_time = None
        self.__is_running = False
        self.__train_building_message_ts = None
        self.__train_building_message_channel = None

        self.__notification_weekdays: Dict[str, bool] = {
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        for v in notification_weekdays:
            self.__notification_weekdays[str(v).lower().strip()] = True
        self.t1 = Thread(target=self.task)

    def run(self) -> None:
        self.__is_running = True
        self.t1.start()

    def stop(self) -> None:
        self.__is_running = False
        self.t1.join()

    def is_running(self) -> bool:
        return self.__is_running

    def get_selected_time(self) -> None:
        return self.__selected_time

    def set_selected_time(self, selected_time: Any) -> None:
        self.__selected_time = selected_time

    def set_client(self, client: Any) -> None:
        self.__client = client

    def set_channel_name(self, channel_name: Any) -> None:
        self.__channel_name = channel_name

    def set_compute_lunch_datetime(self, compute_lunch_datetime: Any) -> None:
        self.__compute_lunch_datetime = compute_lunch_datetime

    def set_participants_notification_datetime(
        self, participants_notification_datetime: Any
    ) -> None:
        self.__participants_notification_datetime = participants_notification_datetime

    def get_participants_notification_datetime(self) -> Any:
        return self.__participants_notification_datetime

    def get_compute_lunch_datetime(self) -> Any:
        return self.__compute_lunch_datetime

    def set_notification_weekdays(self, notification_weekdays: List[str]) -> None:
        self.__notification_weekdays = {
            "monday": False,
            "tuesday": False,
            "wednesday": False,
            "thursday": False,
            "friday": False,
            "saturday": False,
            "sunday": False,
        }
        for v in notification_weekdays:
            self.__notification_weekdays[str(v).lower().strip()] = True

    def get_notification_weekdays(self) -> Dict:
        return self.__notification_weekdays

    # TODO Reduce complexity 19
    def task(self) -> None:  # NOQA: C901
        global USERS_PARTICIPATING
        global USERS_NOT_PARTICIPATING
        global USER_TIME_PREFERENCES
        global USER_RESTAURANT_PREFERENCES
        global PARTICIPANTS_PRIVATE_MESSAGES
        global SELECTED_TIME
        global SELECTED_RESTAURANT
        global TIME_DISSATISFIED_USERS
        global RESTAURANT_DISSATISFIED_USERS
        while self.is_running():
            # move to the next day if the current __participants_notification_datetime is in the past
            time_diff = (
                self.__participants_notification_datetime - datetime.datetime.utcnow()
            )
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
            # sleep 1 second then check if __participants_notification_datetime is changed or
            # the task is no more running

            time_diff = (
                self.__participants_notification_datetime - datetime.datetime.utcnow()
            )
            time_diff_seconds = time_diff.total_seconds()
            while time_diff_seconds > 0:
                if not self.__is_running:
                    return
                if time_diff_seconds < 0:
                    break
                sleep(1)
                time_diff = (
                    self.__participants_notification_datetime
                    - datetime.datetime.utcnow()
                )
                time_diff_seconds = time_diff.total_seconds()

            try:
                # start the train building notification
                if self.__client is not None and self.__channel_name is not None:
                    response = self.__client.chat_postMessage(
                        channel=self.__channel_name,
                        text="Building up new lunch train",
                        blocks=create_participating_message(),
                    )

                    if "ok" in response and "ts" in response and "channel" in response:
                        self.__train_building_message_ts = response["ts"]
                        self.__train_building_message_channel = response["channel"]
            except Exception as e:
                loguru.logger.error(e)

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

            try:
                # Closing the train
                if self.__client is not None and self.__channel_name is not None:
                    self.__client.chat_delete(
                        channel=self.__train_building_message_channel,
                        ts=self.__train_building_message_ts,
                    )
                    _compute_selected_parameters(self.__client)
                    self.__client.chat_postMessage(
                        channel=self.__train_building_message_channel,
                        text="Closing lunch train",
                        blocks=close_train_message(self.__client),
                    )
            except Exception as e:
                loguru.logger.error(e)

            self.__participants_notification_datetime += datetime.timedelta(days=1)
            while (
                self.get_notification_weekdays()[
                    WEEKDAY_NUMBER_TO_STRING[
                        self.__participants_notification_datetime.weekday()
                    ]
                ]
                is False
            ):
                self.__participants_notification_datetime += datetime.timedelta(days=1)

            self.__compute_lunch_datetime += datetime.timedelta(days=1)
            while (
                self.get_notification_weekdays()[
                    WEEKDAY_NUMBER_TO_STRING[self.__compute_lunch_datetime.weekday()]
                ]
                is False
            ):
                self.__compute_lunch_datetime += datetime.timedelta(days=1)

            USERS_PARTICIPATING = []
            USERS_NOT_PARTICIPATING = []
            USER_TIME_PREFERENCES = {}
            USER_RESTAURANT_PREFERENCES = {}
            PARTICIPANTS_PRIVATE_MESSAGES = {}
            SELECTED_TIME = None
            SELECTED_RESTAURANT = None
            TIME_DISSATISFIED_USERS = []
            RESTAURANT_DISSATISFIED_USERS = []


def add_participating_user(user_id: Any) -> None:
    if user_id not in USERS_PARTICIPATING:
        USERS_PARTICIPATING.append(user_id)
    if user_id in USERS_NOT_PARTICIPATING:
        USERS_NOT_PARTICIPATING.remove(user_id)
    if user_id not in USER_RESTAURANT_PREFERENCES:
        USER_RESTAURANT_PREFERENCES[user_id] = []
    if user_id not in USER_TIME_PREFERENCES:
        USER_TIME_PREFERENCES[user_id] = []


def remove_participating_user(user_id: Any) -> None:
    if user_id in USERS_PARTICIPATING:
        USERS_PARTICIPATING.remove(user_id)
    if user_id not in USERS_NOT_PARTICIPATING:
        USERS_NOT_PARTICIPATING.append(user_id)


def add_message_to_participants(message_ts: Any, user_id: Any, channel: Any) -> None:
    PARTICIPANTS_PRIVATE_MESSAGES[user_id] = (message_ts, channel)


def get_participants_message(user_id: Any) -> Optional[Tuple]:
    if user_id in PARTICIPANTS_PRIVATE_MESSAGES:
        return PARTICIPANTS_PRIVATE_MESSAGES[user_id]  # type: ignore
    return None


def add_user_time_preferences(user_id: Any, time: Any) -> None:
    if user_id not in USER_TIME_PREFERENCES:
        USER_TIME_PREFERENCES[user_id] = []
    if time not in USER_TIME_PREFERENCES[user_id]:
        USER_TIME_PREFERENCES[user_id].append(time)


def remove_user_time_preferences(user_id: Any, time: Optional[str] = None) -> None:
    if time is None or user_id in USER_TIME_PREFERENCES:
        USER_TIME_PREFERENCES[user_id] = []
    if time in USER_TIME_PREFERENCES[user_id]:
        USER_TIME_PREFERENCES[user_id].remove(time)


def add_user_restaurant_preferences(user_id: Any, restaurant: Any) -> None:
    if user_id not in USER_RESTAURANT_PREFERENCES:
        USER_RESTAURANT_PREFERENCES[user_id] = []
    if restaurant not in USER_RESTAURANT_PREFERENCES[user_id]:
        USER_RESTAURANT_PREFERENCES[user_id].append(restaurant)


def remove_user_restaurant_preferences(
    user_id: Any, restaurant: Optional[str] = None
) -> None:
    if restaurant is None or user_id not in USER_RESTAURANT_PREFERENCES:
        USER_RESTAURANT_PREFERENCES[user_id] = []
    if restaurant in USER_RESTAURANT_PREFERENCES[user_id]:
        USER_RESTAURANT_PREFERENCES[user_id].remove(restaurant)


# TODO Reduce complexity 19
def _compute_selected_parameters(client: Any) -> None:  # noqa: C901
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

    if len(time_preferences_score) > 0:
        time_preference = sorted(
            time_preferences_score.items(), key=lambda x: x[1], reverse=True
        )[0]
        time_dissatisfied_users_local = []
        if int(time_preference[1]) < user_count:
            # find users that hadn't selected the time preference
            for user, time_preferences in USER_TIME_PREFERENCES.items():
                if time_preference[0] not in time_preferences:
                    time_dissatisfied_users_local.append(
                        get_user_info_from_client(client, user)["name"]
                    )
        SELECTED_TIME = time_preference[0]
        TIME_DISSATISFIED_USERS = time_dissatisfied_users_local

    if len(restaurant_preferences_score) > 0:
        restaurant_preference = sorted(
            restaurant_preferences_score.items(), key=lambda x: x[1], reverse=True
        )[0]
        restaurant_dissatisfied_users_local = []
        if int(restaurant_preference[1]) < user_count:
            # find users that hadn't selected the restaurant preference
            for user, restaurant_preferences in USER_RESTAURANT_PREFERENCES.items():
                if restaurant_preference[0] not in restaurant_preferences:
                    restaurant_dissatisfied_users_local.append(
                        get_user_info_from_client(client, user)["name"]
                    )
        SELECTED_RESTAURANT = restaurant_preference[0]
        RESTAURANT_DISSATISFIED_USERS = restaurant_dissatisfied_users_local
    return


def get_user_info_from_client(client: Any, user_id: Any) -> Dict:
    user_info = client.users_info(user=str(user_id))
    if (
        user_info
        and "ok" in user_info
        and user_info["ok"] is True
        and "user" in user_info
    ):
        return user_info["user"]  # type: ignore
    return {}
