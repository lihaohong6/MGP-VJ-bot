import asyncio
import json
import logging
import pickle
import re
import urllib.parse
from dataclasses import dataclass
from typing import List, Optional

import pywikibot
import requests
from bs4 import BeautifulSoup
from pywikibot import Page

import string_utils
from config.config import replacement_redo_limit
from japanese_utils import get_invalid_furigana
from models.conversion_log import ConversionLog, ConversionList
from models.lyrics import Word, Type
from string_utils import find_in_string
from utils.caching import save_object, load_object
from utils.input_utils import prompt_choices
from utils.japanese_char import is_kanji, get_pronunciations


@dataclass
class MGPPage:
    pwb_page: Page
    song_names: List[str]
    wikitext: str

    def __init__(self, title: str, site=pywikibot.Site()):
        self.pwb_page = Page(site, title)
        self.wikitext = self.pwb_page.text

    @property
    def id(self) -> str:
        return str(self.pwb_page.pageid)

    @property
    def title(self) -> str:
        return self.pwb_page.title(underscore=True, with_ns=False, with_section=False)

    def __str__(self):
        return "page {} with id {}".format(self.title, self.id)


def get_pages_in_cat(cat: str) -> list[str]:
    """
    Get all pages in a certain category.
    :param cat: Name of the category
    :return: A list of page names in this category.
    """
    result = []
    url = "https://zh.moegirl.org.cn/api.php?action=query&list=categorymembers&format=json&cmnamespace=0" \
          f"&cmtitle=Category:{urllib.parse.quote(cat)}" \
          "&cmlimit=500&cmcontinue={}"
    prev = ""
    page_num = 1
    while True:
        response = json.loads(requests.get(url.format(prev)).text)
        logging.info("Processing page {}".format(page_num))
        page_list = response['query']['categorymembers']
        for page in page_list:
            result.append(page['title'])
        if 'continue' not in response:
            return result
        prev = response['continue']['cmcontinue']
        page_num += 1


def get_vocaloid_japan_pages() -> list[str]:
    """
    Find the intersection of VOCALOID songs and Japanese songs.
    :return: A list of song names
    """
    result_vocaloid = get_pages_in_cat("使用VOCALOID的歌曲")
    result_japan = set(get_pages_in_cat("日本音乐作品"))
    return [song_name for song_name in result_vocaloid
            if song_name in result_japan]


def get_titles(text: str, existing: list[str]) -> list[str]:
    """
    Extract titles from a page
    :param text: The wikitext of this page
    :param existing: Existing known titles
    :return: A list of possible song names for this page
    """
    indices = find_in_string(text, ["|歌曲名称", "="])
    if len(indices) < 2:
        return existing
    index_end = string_utils.find_symbol_not_in_bracket(text, '|', indices[1])
    if index_end == -1:
        return existing
    names = text[indices[1] + 1:index_end].strip()
    # split by line break
    parts = re.split("<br */?>", names)
    for part in parts:
        # remove html tags such as <span>
        part = BeautifulSoup(part, "html.parser").text
        # remove templates such as {{lj}} or {{lang}}
        indices = find_in_string(part, ["{{", "|", "}}"])
        if len(indices) == 3:
            existing.append(part[indices[0] + 2:indices[2]].split("|")[-1].strip())
            continue
        existing.append(part.strip())
    return list(set(existing))


def get_page(page_name: str) -> MGPPage:
    # Note: pages are not cached (for now)
    cache_filename = "MGPPage" + page_name + ".txt"
    page: MGPPage = load_object(cache_filename)
    if page is None:
        page = MGPPage(page_name)
        page.song_names = get_titles(page.wikitext, [page.title])
        # save_object(cache_filename, pickle.dumps(page))
    return page


def filter_invalid_furigana(words: list[Word], conversions: ConversionList, log: ConversionLog) -> list[Word]:
    invalid_furigana: ConversionList = list(set(get_invalid_furigana(conversions)))
    if len(invalid_furigana) == 0:
        return words
    remove = []
    while len(invalid_furigana) > 0:
        options = ["{}: {} => {}".format(before.surface, before.hiragana, after.hiragana)
                   for before, after in invalid_furigana]
        options.append("All good.")
        response = prompt_choices("Select a conversion to remove", options)
        if response == len(options):
            break
        remove.append(invalid_furigana.pop(response - 1))
    for before, after in remove:
        index_start = 0
        while after in words[index_start:]:
            index = words.index(after, index_start)
            words[index] = before
            index_start = index + 1
    log.removed_conversions = remove
    return words


def replace(jap: str, words: list[Word], logs: ConversionLog) -> Optional[str]:
    words_original = list(words)
    prev = 0
    result = []
    index = 0
    bracket = 0
    redo = 0
    while index < len(jap):
        ch = jap[index]
        if index > 0 and jap[index] == jap[index - 1]:
            if jap[index] == '{':
                bracket += 1
            elif jap[index] == '}':
                bracket -= 1
        if not is_kanji(ch) or bracket > 0:
            index += 1
            continue
        result.append(jap[prev:index])
        while True:
            if len(words) == 0:
                if redo > replacement_redo_limit:
                    return None
                redo += 1
                words = list(words_original)
            word = words.pop(0)
            surface = word.surface
            if jap[index:index + len(surface)] == surface:
                index += len(surface)
                prev = index
                if string_utils.is_empty(word.hiragana):
                    result.append(word.surface)
                else:
                    logs.word_used(word)
                    result.append("{{{{photrans|{}|{}}}}}".format(word.surface, word.hiragana))
                break
    result.append(jap[prev:])
    return "".join(result)


def replace_lyrics_jap(jap: str, words: list[Word], logs: ConversionLog) -> Optional[str]:
    words = [w for w in words if w.type == Type.KANJI]
    res = replace(jap, words, logs)
    if res is None:
        return None
    words = filter_invalid_furigana(logs.all_words, logs.word_conversions, logs)
    logs.used_conversions = []
    return replace(jap, words, logs)


edit_lock = asyncio.Lock()


def save_edit(text: str, page: MGPPage, logs: ConversionLog) -> bool:
    logging.info(
        "Pushing changes of " + str(page) +
        " url https://zh.moegirl.org.cn/" + urllib.parse.quote(page.title))
    page.pwb_page.text = text
    logs_list = ["{}:{}=>{}".format(w1.surface, w1.hiragana, w2.hiragana)
                 for w1, w2 in logs.used_conversions if w2.hiragana not in get_pronunciations(w2.surface)]
    logs_list = list(set(logs_list))
    logs_list.extend(["{}:{}≠>{}".format(w1.surface, w1.hiragana, w2.hiragana)
                      for w1, w2 in logs.removed_conversions])
    summary = "添加注音（由[[User:Lihaohong/注音机器人|机器人]]自动添加）({})".format(";".join(logs_list))
    logging.info(summary)
    if len(logs_list) == 0 or prompt_choices("Save?", ["Yes", "No"]) == 1:
        page.pwb_page.save(summary=summary,
                           watch="watch", minor=False, asynchronous=False, botflag=True)
        return True
    logging.info("Rejected changes proposed to " + page.title)
    return False
