import signal
from pathlib import Path
from time import sleep

from utils.logger import get_logger

keep_sleeping: bool


def wake_up():
    global keep_sleeping
    keep_sleeping = False


def sleep_minutes(minute: int):
    global keep_sleeping
    keep_sleeping = True
    signal.signal(signal.SIGINT, wake_up)
    try:
        get_logger().info("Sleeping for " + str(minute) + " minutes")
        counter = 0
        while counter < minute and keep_sleeping:
            sleep(60)
            counter += 1
            get_logger().info("{} minute(s) remaining...".format(minute - counter))
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        return
    except Exception as e:
        get_logger().info("Sleep interrupted by " + str(e))
        signal.signal(signal.SIGINT, signal.SIG_DFL)
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


def completed_task(t: str):
    cont = Path("continue.txt")
    signal.signal(signal.SIGINT, signal.SIG_IGN)
    with open(cont, "w") as f:
        f.write(str(t))
        f.flush()
    signal.signal(signal.SIGINT, signal.SIG_DFL)
