from enum import Enum


class Mode(Enum):
    AUTO_FURIGANA = 0
    AUTO_YOUTUBE_FALLBACK = 1
    AUTO_LYRICS_KAI = 2
    BILIBILI_VIDEO = 3


waf_sleep: int = 15
mode: Mode = Mode.AUTO_LYRICS_KAI
line_strict: bool = False
skip_words_in_replacement: int = 3
replacement_redo_limit = 5
alert_input = False
ignore_minor_diff = True


def get_mode() -> Mode:
    return mode
