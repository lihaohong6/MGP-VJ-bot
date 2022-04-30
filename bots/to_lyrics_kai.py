import dataclasses
import re

import wikitextparser as wtp
from wikitextparser import Template

from bots.common import run_vj_bot, run_with_waf
from bots.youtube_fallback import transform_wikitext
from utils.input_utils import prompt_response, prompt_choices
from utils.japanese_utils import furigana_local
from utils.logger import get_logger
from utils.string_utils import is_empty
from utils.wikitext import get_template_by_name
from web.mgp import get_page, save_edit

hover: bool = True
add_furigana: bool = False


@dataclasses.dataclass()
class Lyrics:
    original: str
    translated: str
    roma: str = None
    color_left: str = "#000000"
    color_right: str = "#000000"
    author: str = None
    hide_disclaimer: bool = False
    lang_original: str = "ja"


def force_same_line_number(left: str, right: str) -> (str, str):
    left_lines = left.count("\n")
    right_lines = right.count("\n")
    line_count = max(left_lines, right_lines)
    left += "\n" * (line_count - left_lines)
    right += "\n" * (line_count - right_lines)
    return left, right


def remove_lyrics_whitespace(original: str, translated: str) -> (str, str):
    lines1 = original.split("\n")
    lines2 = translated.split("\n")
    res1 = []
    res2 = []
    empty = False
    min_len = min(len(lines1), len(lines2))
    for i in range(min_len):
        if is_empty(lines1[i]) and is_empty(lines2[i]):
            empty = True
            continue
        if empty:
            empty = False
            res1.append("")
            res2.append("")
        res1.append(lines1[i])
        res2.append(lines2[i])
    if res1[0] == '' and res2[0] == '':
        res1, res2 = res1[1:], res2[1:]
    res1.extend(lines1[min_len:])
    res2.extend(lines2[min_len:])
    return "\n".join(res1), "\n".join(res2)


def add_no_hover(original: str, translated) -> (str, str):
    if not hover:
        return original, translated
    lines1 = original.split("\n")
    lines2 = translated.split("\n")
    for i in range(len(lines1)):
        if is_empty(lines1[i]) or len(lines2) <= i or is_empty(lines2[i]):
            lines1[i] += "#NoHover"
    return "\n".join(lines1), "\n".join(lines2)


def expand_br(lyrics: str) -> str:
    lyrics = lyrics.rstrip()
    result, replacements = re.subn("<br */? *>", "\n", lyrics)
    return result if replacements > 0 else lyrics


def post_process_start(lyrics: str) -> str:
    lyrics = list(lyrics)
    for index, char in enumerate(lyrics):
        if char == "\n":
            lyrics[index] = "<br/>"
        else:
            break
    return "".join(lyrics)


def post_process_lyrics(original: str, translated: str) -> (str, str):
    original, translated = expand_br(original), expand_br(translated)
    original, translated = force_same_line_number(original, translated)
    original, translated = remove_lyrics_whitespace(original, translated)
    original, translated = add_no_hover(original, translated)
    if add_furigana:
        original = furigana_local(original)
    return post_process_start(original), post_process_start(translated)


def lyrics_to_lyrics_kai(lyrics: Lyrics, song_name: str) -> str | None:
    if lyrics.hide_disclaimer or lyrics.author:
        get_logger().warning("Lyrics for song " + song_name + " contains special information.")
        return None
    original, translated = post_process_lyrics(lyrics.original, lyrics.translated)
    lines = [
        "{{LyricsKai" + ("/hover" if hover else ""),
        "|lstyle=color:" + lyrics.color_left,
        "|rstyle=color:" + lyrics.color_right,
        "|llang=" + lyrics.lang_original,
        "|original=" + original,
        "|translated=" + translated,
        "}}"
    ]
    return "\n".join(lines)


def lyrics_to_lyrics(lyrics: Template) -> Lyrics:
    original = []
    translated = []
    for i in range(1, 10000):
        left_arg, right_arg = f"lb-text{i}", f"rb-text{i}"
        if not lyrics.has_arg(left_arg):
            break
        left = lyrics.get_arg(left_arg).value
        if lyrics.has_arg(right_arg):
            right = lyrics.get_arg(right_arg).value
        else:
            right = ""
        left, right = force_same_line_number(left, right)
        original.append(left)
        translated.append(right)
    arg_list = [("color_left", "lb-color"),
                ("color_right", "rb-color"),
                ("lang_original", "lang"),
                ("hide_disclaimer", "override"),
                ("author", "author")]
    args = {}
    for arg in arg_list:
        argument = lyrics.get_arg(arg[1])
        if argument is None or is_empty(argument.value):
            continue
        args[arg[0]] = argument.value.strip()
    return Lyrics("\n".join(original), "\n".join(translated),
                  **args)


def convert_lyrics(lyrics: Template, song_name) -> str:
    return lyrics_to_lyrics_kai(lyrics_to_lyrics(lyrics), song_name)


def transform_wikitext(text, song_name) -> str | None:
    parsed = wtp.parse(text)
    lyrics = get_template_by_name(parsed, "Lyrics")
    changed = False
    for t in lyrics:
        res = convert_lyrics(t, song_name)
        if res is not None:
            t.string = res
            changed = True
    return str(parsed) if changed else None


def process_song(song_name: str):
    page = get_page(song_name)
    res = transform_wikitext(page.wikitext, song_name)
    if res is None:
        return
    wikitext = str(res)
    save_edit(wikitext, page,
              "由[[User:Lihaohong/LyricsKai转换工具|半自动工具]]自动使用[[T:LyricsKai" + ("/hover" if hover else "") + "]]模板",
              confirm=False, minor=True, watch="watch")


def manual():
    while True:
        page_name = prompt_response("Page name?")
        if is_empty(page_name):
            return
        if page_name == "config":
            global add_furigana
            add_furigana = 1 == prompt_choices("Add furigana?", ["Yes", "No"])
        run_with_waf(process_song, page_name)


def lyrics_kai():
    run_vj_bot(process_song, manual)
