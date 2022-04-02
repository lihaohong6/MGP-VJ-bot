import pickle
from pathlib import Path
from typing import Optional, Union

cache_path = Path("./cache")


def init_caching():
    cache_path.mkdir(exist_ok=True)


def get_cache(filename: str) -> Optional[str]:
    try:
        f = open(cache_path.joinpath(filename), "r", encoding="utf-8")
        content = f.read()
        f.close()
        return content
    except FileNotFoundError:
        return None


def save_cache(filename: str, content: str):
    with open(cache_path.joinpath(filename), "w", encoding="utf-8") as f:
        f.write(content)


def save_object(filename: str, content):
    with open(cache_path.joinpath(filename), "wb") as f:
        pickle.dump(content, f)


def load_object(filename: str):
    try:
        with open(cache_path.joinpath(filename), "rb") as f:
            return pickle.load(f)
    except FileNotFoundError:
        return None
