from pathlib import Path
from time import sleep

from utils.logger import get_logger


def sleep_minutes(minute: int):
    try:
        get_logger().info("Sleeping for " + str(minute) + " minutes")
        counter = 0
        while counter < minute:
            sleep(60)
            counter += 1
            get_logger().info("{} minute(s) remaining...".format(minute - counter))
        return
    except Exception as e:
        get_logger().info("Sleep interrupted by " + str(e))
        return


def get_resume_index(lst: list) -> int:
    index = 0
    cont = Path("continue.txt")
    if cont.exists():
        with open(cont, "r") as f:
            start = f.readline().strip()
        while lst[index] != start:
            index += 1
        index += 1
    get_logger().info("Resuming with " + str(lst[index]))
    return index