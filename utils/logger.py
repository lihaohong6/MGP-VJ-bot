import logging
import sys
from pathlib import Path

logger = logging.getLogger()


def setup_logger():
    global logger
    logger = logging.getLogger("application")
    logger.setLevel(logging.DEBUG)
    handler = logging.StreamHandler(sys.stdout)
    handler.setLevel(logging.INFO)
    logger.addHandler(handler)
    handler = logging.FileHandler("logs.txt")
    handler.setLevel(logging.DEBUG)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)-8s %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)
    handler = logging.FileHandler("warnings.txt")
    handler.setLevel(logging.WARNING)
    handler.setFormatter(logging.Formatter("%(asctime)s %(name)s %(levelname)-5s %(message)s", "%Y-%m-%d %H:%M:%S"))
    logger.addHandler(handler)


def log_str(target: str, text: str):
    path = Path(target)
    path.touch(exist_ok=True)
    with open(path, "a") as f:
        f.write(text)
        f.write("\n")


def get_logger():
    return logger
