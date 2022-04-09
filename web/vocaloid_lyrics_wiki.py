import json
from typing import Optional
from urllib.parse import quote

import requests
from bs4 import BeautifulSoup

from utils.japanese_utils import lyrics_match
from models.conversion_log import ConversionLog
from utils.logger import get_logger
from utils.string_utils import is_empty
from utils.japanese_char import is_punctuation_or_half_width_katakana, \
    is_english_punctuation


def search(name: str, producer: str) -> list[str]:
    if is_empty(name):
        return []
    try:
        url = "https://vocaloidlyrics.fandom.com/api.php?action=opensearch&search={}"
        url = url.format(quote(name))
        response = json.loads(requests.get(url).text)
        _, names, _, urls = response
        if len(names) == 0:
            return []
        return urls[0:min(5, len(urls))]
    except Exception as e:
        get_logger().error("Could not search on vocaloid lyrics wiki using keyword " + name + ". " + str(e))


def process_japanese(j) -> str:
    # remove ruby top
    ruby_top = j.find_all('rt')
    for t in ruby_top:
        t.decompose()
    sup = j.find_all('sup')
    for t in sup:
        t.decompose()
    j: str = j.text
    return "".join([" " if is_punctuation_or_half_width_katakana(c)
                           or is_english_punctuation(c)
                    else c
                    for c in j])


def process_romaji(romaji) -> str:
    text: str = romaji.text
    text = text.lower()
    replace = [('ā', 'aa'), ('ō', 'ou'), ('ū', 'uu'), ('ī', 'i'), ('ē', 'ei')]
    for r in replace:
        text = text.replace(r[0], r[1])
    return text


def retrieve_lyrics_from_page(url: str) -> Optional[tuple[str, str]]:
    response = requests.get(url).text
    soup = BeautifulSoup(response, "html.parser")
    content = soup.find("div", {"id": "mw-content-text"})
    targets = [('table', {"class": "lyrics"}),
               ("table", {"style": "width:100%"}),
               ("table", {"width": "100%"}),
               ("table", {})]
    lyrics = None
    for target in targets:
        lyrics = content.find(target[0], target[1])
        if lyrics is not None:
            break
    if lyrics is None:
        return None
    lines = list(lyrics.find_all("tr"))[1:]
    japanese_list = []
    romaji_list = []
    for line in lines:
        columns = line.find_all("td")
        if len(columns) >= 2:
            japanese, romaji, *rest = columns
        else:
            continue
        japanese_list.append(process_japanese(japanese))
        romaji_list.append(process_romaji(romaji))
    return "".join(japanese_list), "".join(romaji_list)


def get_romaji(names: list[str], lyrics_jap: str, logs: ConversionLog, producer: str = None) -> Optional[tuple[list[str], list[str]]]:
    """
    Search Vocaloid Lyrics Wiki for a song.
    :param names: A list of possible names for the song. Each name will be searched.
    :param lyrics_jap: The expected Japanese lyrics.
    :param logs: logging class
    :param producer: Not used. Could use this to further disambiguate songs with the same name.
    :return: If found, a tuple of (1) a list of Japanese lyrics line by line (2) a list of romaji line by line
    Otherwise, return None
    """
    # find all urls given by the search result
    urls = set()
    for name in names:
        res = search(name, producer)
        for r in res:
            urls.add(r)
    # for each url, try to retrieve the lyrics from the page
    for url in urls:
        res = retrieve_lyrics_from_page(url)
        if res is None:
            continue
        jap, romaji = res
        # if the japanese lyrics matches the expected japanese lyrics, the correct song is
        # found, so return
        if lyrics_match(lyrics_jap, jap, logs):
            jap_list = jap.split("\n")
            romaji_list = romaji.split("\n")
            # FIXME: whether spaces and other special characters are kept should be
            #   decided later
            # filter out special characters in romaji
            return jap_list, ["".join([c for c in line if c.isalnum()]) for line in romaji_list]
    return None
