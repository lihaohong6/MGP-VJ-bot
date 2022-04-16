import logging
import re
from re import Match
from typing import Optional, Callable

from wikitextparser import Argument, Template

from bots.common import run_vj_bot, run_with_waf
from utils.helpers import get_resume_index, completed_task
from utils.input_utils import prompt_choices, prompt_response
from utils.logger import get_logger, log_str
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


def pattern1(other_info: str, match: Match) -> Optional[tuple[int, int]]:
    num_start = match.end()
    num_match = re.search("[0-9,]+", other_info[num_start:])
    if num_match.start() >= 2:
        return None
    num_end = num_match.end() + num_start
    if len(other_info) > num_end and other_info[num_end] == '+':
        num_end += 1
    return num_start, num_end


def pattern2(text: str, match: Match) -> Optional[tuple[int, int]]:
    num_start = match.start()
    parenthesis = re.search("[+]?[(（]", text[num_start:])
    num_end = num_start + parenthesis.start()
    if text[num_end] == '+':
        num_end += 1
    return num_start, num_end


def pattern3(text: str, match: Match) -> Optional[tuple[int, int]]:
    return match.start() + 1, match.end()


Pattern = Callable[[str, Match], Optional[tuple[int, int]]]
patterns: dict[str, Pattern] = {
    "[Yy]ou[Tt]ube.?.?.?[，,]?(再生|播放)[数數量]?[为為]?": pattern1,
    "[0-9][0-9,]+[+]?[(（][Yy]ou[Tt]ube": pattern2,
    "[和、，][0-9][0-9,]+[+]": pattern3
}


def find_youtube_count(text: str, song_name: str = "Unknown", log_error: bool = True) -> Optional[tuple[int, int]]:
    log_file = "revisit.txt"
    if "删" in text or "最终记录" in text or "重制" in text or "补档" in text:
        if log_error:
            get_logger().warning("For page " + song_name + ": suspected re-upload. " + text)
            log_str(log_file, song_name)
        return None
    for pattern, func in patterns.items():
        match = re.search(pattern, text)
        if match is not None:
            res = func(text, match)
            if res is None:
                continue
            return res
    if log_error:
        get_logger().error("For page " + song_name + ": cannot find pattern in " + text)
        log_str(log_file, song_name)
    return None


def add_youtube_count(song_box: Template, song_name: str) -> bool:
    yt_id = song_box.get_arg("yt_id")
    other_info = song_box.get_arg("其他资料")
    if yt_id is None or other_info is None or re.search("[Yy]ou[Tt]ube", other_info.value) is None:
        return False
    yt_id = yt_id.value.strip()
    # try to find the raw view count
    yt_views = get_yt_views(yt_id)
    if yt_views is None:
        return False
    res = find_youtube_count(other_info.value, song_name, log_error=True)
    if res is None:
        return False
    num_start, num_end = res
    template = "{{" + f"YoutubeCount|id={yt_id}" + "}}"
    other_info.value = other_info.value[:num_start] + template + other_info.value[num_end:]
    return True


def transform_wikitext(song_name: str, wikitext: str) -> Optional[WikiText]:
    parsed = wtp.parse(wikitext)
    song_boxes = get_template_by_name(parsed, "VOCALOID_Songbox")
    changed = False
    for song_box in song_boxes:
        yt_count_list = get_template_by_name(song_box, "YoutubeCount")
        if len(yt_count_list) == 0:
            res = add_youtube_count(song_box, song_name)
            changed = res or changed
            continue
        # disabled because no longer needed
        # for yt_count in yt_count_list:
        #     res = update_yt_count(yt_count, song_name)
        #     changed = res or changed
    return parsed if changed else None


def process_song(song_name: str):
    page = get_page(song_name)
    res = transform_wikitext(song_name, page.wikitext)
    if res is None:
        return
    wikitext = str(res)
    save_edit(wikitext, page, "由[[User:Lihaohong/再生机器人|机器人]]自动添加YoutubeCount模板",
              confirm=False, minor=True, watch="nochange")


def youtube_fallback():
    run_vj_bot(process_song)
