import logging
from json import JSONDecodeError
from typing import Callable, Any

from pywikibot.exceptions import SiteDefinitionError, OtherPageSaveError

from utils.helpers import completed_task, get_resume_index, sleep_minutes
from utils.input_utils import prompt_choices, prompt_response
from utils.logger import get_logger
from utils.string_utils import is_empty
from web.mgp import fetch_vj_songs


def run_vj_bot(processor: Callable[[str], Any], manual: Callable = None):
    if manual is None:
        manual = get_manual_mode(processor)
    choice = prompt_choices("Mode?", ["Manual", "Auto"])
    if choice == 1:
        manual()
        return
    songs: list[str] = fetch_vj_songs()
    # continue from where the bot stopped last time
    index = get_resume_index(songs)
    while index < len(songs):
        # process the current song in the list
        song = songs[index]
        run_with_waf(processor, song)
        # this song has been finished; disallow SIGINT while file io in progress
        completed_task(song)
        index += 1


def run_with_waf(func: Callable[[str], None], page_name: str):
    retries = 3
    while retries > 0:
        try:
            func(page_name)
            return
        except Exception as e:
            get_logger().error("For page " + page_name)
            if isinstance(e, JSONDecodeError) or \
                    isinstance(e, SiteDefinitionError) or \
                    isinstance(e, OtherPageSaveError):
                if "腾讯" in repr(e):
                    get_logger().error("{}.".format(e.__class__) +
                                       "MGP is probably unreachable due to WAF or DDOS. Will try again in 10 minutes.")
                    sleep_minutes(15)
                else:
                    get_logger().error("", exc_info=e)
                    retries -= 1
            else:
                get_logger().error("", exc_info=e)
                retries -= 1


def get_manual_mode(process_page: Callable[[str], None]):
    def manual_mode():
        while True:
            page_name = prompt_response("Page name?")
            if is_empty(page_name):
                return
            run_with_waf(process_page, page_name)

    return manual_mode
