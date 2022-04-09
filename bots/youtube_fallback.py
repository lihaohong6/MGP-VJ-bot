import logging
import re
from typing import Optional

from wikitextparser import Argument, Template

from bots.common import run_bot, run_with_waf
from utils.helpers import get_resume_index, completed_task
from utils.input_utils import prompt_choices, prompt_response
from utils.logger import get_logger
from utils.string_utils import is_empty
from utils.wikitext import get_template_by_name, title_equal
from web.mgp import fetch_vj_songs, get_page, save_edit
import wikitextparser as wtp
from wikitextparser import WikiText

from web.youtube import get_yt_views


def convert_views(views: int, fallback: str) -> Optional[int]:
    changed = False
    if not fallback.isdigit():
        fallback = "".join([c for c in fallback if c.isdigit()])
        changed = True
    fallback = int(fallback)
    if views / fallback >= 1.2:
        fallback = views
        changed = True
    if not changed:
        get_logger().info("Fallback: {}; current: {}. No need to update.".format(fallback, views))
        return None
    return fallback


def update_yt_count(yt_count: Template, song_name: str) -> bool:
    fallback = yt_count.get_arg("fallback")
    vid = yt_count.get_arg("id")
    if vid is None:
        get_logger().warning(song_name + " has no id in YT Count template.")
        return False
    if fallback is None:
        fallback = Argument("|fallback=1")
    views = get_yt_views(vid.value)
    if views is None:
        get_logger().warning("Cannot fetch YT views for " + song_name)
        return False
    result = convert_views(views, fallback.value)
    if result is None:
        return False
    result = str(result)
    yt_count.set_arg("fallback", result)
    return True


def add_youtube_count(song_box: Template) -> bool:
    yt_id = song_box.get_arg("yt_id")
    other_info = song_box.get_arg("其他资料")
    if yt_id is None or other_info is None:
        return False
    yt_id = yt_id.value.strip()
    # try to find the raw view count
    youtube_occurrence = len(re.findall("[Yy]ou[Ttube]", other_info.value))
    if youtube_occurrence != 1:
        if youtube_occurrence > 1:
            get_logger().warning("Youtube appeared more than once in " + other_info.value + ", skipping...")
        return False
    youtube_match = re.search("[Yy]ou[Tt]ube，?再生[数數]为", other_info.value)
    if youtube_match is None:
        get_logger().error("YT Id " + yt_id + " found but no YT text in " + other_info.value)
        return False
    yt_views = get_yt_views(yt_id)
    if yt_views is None:
        return False
    num_start = youtube_match.end()
    num_match = re.search("[0-9,]+", other_info.value[num_start:])
    if num_match is None or num_match.start() >= 2:
        # number does not immediately follow string
        return False
    num_end = num_start + num_match.end()
    template = "{{" + f"YoutubeCount|id={yt_id}|fallback={yt_views}" + "}}"
    other_info.value = other_info.value[:num_start] + template + other_info.value[num_end:]
    return True


def transform_wikitext(song_name: str, wikitext: str) -> Optional[WikiText]:
    parsed = wtp.parse(wikitext)
    song_boxes = get_template_by_name(parsed, "VOCALOID_Songbox")
    changed = False
    for song_box in song_boxes:
        yt_count_list = get_template_by_name(song_box, "YoutubeCount")
        if len(yt_count_list) == 0:
            res = add_youtube_count(song_box)
            changed = res or changed
            continue
        for yt_count in yt_count_list:
            res = update_yt_count(yt_count, song_name)
            changed = res or changed
    return parsed if changed else None


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
