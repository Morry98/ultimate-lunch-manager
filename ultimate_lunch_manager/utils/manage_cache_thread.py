from threading import Thread
from time import sleep
from typing import List, Callable

from ultimate_lunch_manager.possible_times import possible_times_service
from ultimate_lunch_manager.settings import settings_service
from ultimate_lunch_manager.users import users_service

CACHED_FUNCTION: List[Callable] = [
    possible_times_service.get_time_all_options,
    possible_times_service.get_possible_times,
    users_service.get_users,
    settings_service.get_setting,
    settings_service.get_client,
]


class ManageCacheThread(Thread):
    active = False

    def __init__(self) -> None:
        super().__init__()

    def run(self) -> None:
        while self.active:
            for function in CACHED_FUNCTION:
                function()
            sleep(1)

    def stop(self) -> None:
        self.active = False

    def start(self) -> None:
        self.active = True
        self.run()

    def is_running(self) -> bool:
        return self.active
