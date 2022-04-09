import logging
from typing import Optional

from wikitextparser import Argument

from bots.common import run_bot, run_with_waf
from utils.helpers import get_resume_index, completed_task
from utils.input_utils import prompt_choices, prompt_response
from utils.logger import get_logger
from utils.string_utils import is_empty
from web.mgp import fetch_vj_songs, get_page, save_edit
import wikitextparser as wtp
from wikitextparser import WikiText

from web.youtube import get_yt_views


def convert(yt_id, fallback: str) -> Optional[int]:
    views = get_yt_views(yt_id)
    if views is None:
        get_logger().warning("Cannot fetch YT views for " + yt_id)
        return None
    changed = False
    if not fallback.isdigit():
        fallback = [c for c in fallback if c.isdigit()]
        changed = True
    fallback = int(fallback)
    if views / fallback >= 1.2:
        fallback = views
        changed = True
    return fallback if changed else None


def get_youtube_count_template(parsed) -> Optional:
    yt_count = parsed
    while True:
        templates = [t for t in yt_count.templates if 'YoutubeCount' in t]
        if len(templates) == 0:
            break
        yt_count = templates[0]
        if yt_count.name == 'YoutubeCount':
            break
    if yt_count == parsed:
        return None
    return yt_count


def transform_wikitext(song_name: str, wikitext: str) -> Optional[WikiText]:
    parsed = wtp.parse(wikitext)
    yt_count = get_youtube_count_template(parsed)
    if yt_count is None:
        if "yt_id" in parsed:
            get_logger().info(song_name + " has YT link but no YoutubeCount template")
        else:
            get_logger().info(song_name + " has no YoutubeCount template")
        return
    fb = None
    vid = None
    for arg in yt_count.arguments:
        name = arg.name
        value = arg.value
        if name == 'id':
            vid = value
        if name == 'fallback':
            fb = value
    if vid is None:
        get_logger().warning(song_name + " has no id in YT Count template.")
        return
    if fb is None:
        fb = -1
    result = convert(vid, fb)
    if result is None:
        logging.info("No need to update " + song_name)
        return
    result = str(result)
    for arg in yt_count.arguments:
        if arg.name == 'fallback':
            arg.value = result
            return parsed
    yt_count.arguments.append(Argument("|fallback=" + result))
    return parsed


def process_song(song_name: str):
    page = get_page(song_name)
    res = transform_wikitext(song_name, page.wikitext)
    if res is None:
        return
    wikitext = str(res)
    save_edit(wikitext, page, "由[[User:Lihaohong/再生机器人|机器人]]自动更新YouTube的播放量",
              confirm=False, minor=True, watch="nochange")


def manual_mode():
    while True:
        page_name = prompt_response("Page name?")
        if is_empty(page_name):
            return
        run_with_waf(process_song, page_name)


def youtube_fallback():
    run_bot(process_song, manual_mode)
