import signal
from pathlib import Path
from time import sleep

import config.config
from utils.logger import get_logger

keep_sleeping: bool


def wake_up(sig, frame):
    global keep_sleeping
    keep_sleeping = False


def sleep_minutes(minute: int):
    global keep_sleeping
    keep_sleeping = True
    prev_handler = signal.signal(signal.SIGINT, wake_up)
    try:
        get_logger().info("Sleeping for " + str(minute) + " minutes")
        counter = 0
        while counter < minute and keep_sleeping:
            sleep(60)
            counter += 1
            get_logger().info("{} minute(s) remaining...".format(minute - counter))
        signal.signal(signal.SIGINT, prev_handler)
        return
    except Exception as e:
        get_logger().info("Sleep interrupted by " + str(e))
        signal.signal(signal.SIGINT, prev_handler)
        return


cont_path = Path(f"continue{config.config.get_mode().value}.txt")


def get_resume_index(lst: list) -> int:
    index = 0
    if cont_path.exists():
        with open(cont_path, "r") as f:
            start = f.readline().strip()
        while index < len(lst) and lst[index] != start:
            index += 1
        index += 1
    if index >= len(lst):
        index = 0
    get_logger().info("Resuming with index " + str(index) + ": " + str(lst[index]))
    return index


def completed_task(t: str):
    prev_handler = signal.signal(signal.SIGINT, signal.SIG_IGN)
    with open(cont_path, "w") as f:
        f.write(str(t))
        f.flush()
    signal.signal(signal.SIGINT, prev_handler)
