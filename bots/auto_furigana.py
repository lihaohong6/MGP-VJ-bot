import signal
from json import JSONDecodeError
from time import sleep
from typing import Optional

from pywikibot.exceptions import SiteDefinitionError

import config.config
from bots.common import run_vj_bot
from utils.japanese_char import get_pronunciations
from utils.japanese_utils import is_japanese_lyrics, is_fully_translated, convert_kana
from utils.helpers import sleep_minutes, get_resume_index, completed_task
from models.conversion_log import ConversionLog
from models.lyrics import Type
from utils.input_utils import prompt_response, prompt_choices
from utils.logger import get_logger
from utils.string_utils import extract_lyrics_kai, extract_japanese_lyrics, is_empty
from web.mgp import MGPPage, replace_lyrics_jap, save_edit, get_page, fetch_pages
from web.vocaloid_lyrics_wiki import get_romaji
import wikitextparser as wtp


def convert_page_text(page: MGPPage, log: ConversionLog) -> Optional[str]:
    """
    Add furigana to the text of a MGP page
    :param page: The page object
    :param log: Records of event that happened during conversion
    :return: None if failed. A str object representing the new text if successful.
    """
    # extract the indices of {{LyricsKai...}}
    get_logger().debug("Extracting LyricsKai")
    parsed = wtp.parse(page.wikitext)
    lyrics_kai = None
    need_button = True
    for t in parsed.templates:
        if t.name.lower() == "LyricsKai/Roma/button".lower():
            need_button = False
        if "lyricskai" in t.name.lower() and t.has_arg("original"):
            lyrics_kai = t
    if lyrics_kai is None:
        get_logger().error("Failed to extract LyricsKai from page " + page.title)
    # extract the str of the Japanese lyrics
    lyrics_jap = lyrics_kai.get_arg("original").value
    prepend = ""
    lines = lyrics_jap.split("\n")
    while True:
        if "'''" in lines[0] or is_empty(lines[0]):
            prepend += lines[0] + "\n"
            lines.pop(0)
        else:
            break
    lyrics_jap = "\n".join(lines)
    # decide if the lyrics are in Japanese and if it is already translated
    if not is_japanese_lyrics(lyrics_jap) or is_fully_translated(lyrics_jap):
        get_logger().warning(page.title + ("is not in Japanese. "
                                           if not is_japanese_lyrics(lyrics_jap)
                                           else "is already translated."))
        return None
    # fetch Japanese and romaji lyrics from Vocaloid Lyrics Wiki
    get_logger().debug("Fetching lyrics from Vocaloid Lyrics Wiki")
    vocaloid_lyrics_wiki = get_romaji(page.song_names, lyrics_jap, log)
    if not vocaloid_lyrics_wiki:
        get_logger().warning("Failed to fetch lyrics for " + str(page) + " from Vocaloid Lyrics Wiki.")
        return None
    lyrics_jap_2, romaji = vocaloid_lyrics_wiki
    # match the Japanese lyrics from Vocaloid Lyrics Wiki with
    # romaji from Vocaloid Lyrics Wiki to get a list of words containing
    # the original Kanji and the furigana
    get_logger().debug("Converting lyrics to kana")
    words = convert_kana(lyrics_jap_2, romaji, log, page.id)
    if not words:
        return None
    words = [word for word in words if word.type != Type.KANA]
    # replace Japanese lyrics with the list of words
    get_logger().debug("Replacing original lyrics with photrans")
    lyrics_jap = replace_lyrics_jap(lyrics_jap, words, log)
    if lyrics_jap is None:
        get_logger().warning("Failed to replace original Kanji with photrans for " + str(page))
        return None
    # add photrans button and put everything together
    lyrics_kai.set_arg("original", prepend.lstrip() + lyrics_jap.rstrip())
    if need_button:
        lyrics_kai.string = "{{Photrans/button|float=1}}\n" + lyrics_kai.string
    return str(parsed)


def get_edit_summary(logs: ConversionLog):
    logs_list = ["{}:{}=>{}".format(w1.surface, w1.hiragana, w2.hiragana)
                 for w1, w2 in logs.used_conversions if w2.hiragana not in get_pronunciations(w2.surface)]
    logs_list = list(set(logs_list))
    logs_list.extend(["{}:{}≠>{}".format(w1.surface, w1.hiragana, w2.hiragana)
                      for w1, w2 in logs.removed_conversions])
    logs_list.extend(["{}:?".format(c) for c in set(logs.ignored_kanji)])
    return "添加注音（由[[User:Lihaohong/注音机器人|机器人]]自动添加）({})".format(";".join(logs_list))


def process_page(page: MGPPage) -> bool:
    """
    Process a fetched MGP page
    :param page: Page object to be processed
    :return: True if successful; False otherwise
    """
    # log events during conversion to be shown in edit summary
    logs = ConversionLog()
    text = convert_page_text(page, logs)
    if text:
        return save_edit(text, page, get_edit_summary(logs), confirm=True, minor=False)
    return False


def process_song(page_name: str) -> bool:
    """
    Add furigana to the page.
    :param page_name: Name of the page to change.
    :return: True if successful. False otherwise
    """
    page: Optional[MGPPage] = None
    try:
        # fetch page from MGP
        page = get_page(page_name)
        get_logger().debug("Page titled " + page.title[0] + " loaded.")
        # process page
        return process_page(page)
    except Exception as e:
        if page is None:
            msg = "For page " + page_name
        else:
            msg = "For page title " + page.title + " with id " + page.id + "\n"
        get_logger().error(msg)
        if isinstance(e, JSONDecodeError) or isinstance(e, SiteDefinitionError):
            get_logger().error("{}.".format(e.__class__) +
                               "MGP is probably unreachable due to WAF or DDOS. Will try again in 5 seconds.")
            sleep(5)
            return process_song(page_name)
        else:
            get_logger().error("", exc_info=e)


def manual_mode():
    config.config.alert_input = False
    while True:
        page_id = prompt_response("Page name?")
        if page_id == "0" or not page_id or page_id.isspace():
            return
        result = process_song(page_id)
        get_logger().info("Conversion successful" if result else "Conversion failed.")


def auto_furigana():
    run_vj_bot(process_song)
