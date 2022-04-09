import signal
from json import JSONDecodeError
from typing import Optional

from pywikibot.exceptions import SiteDefinitionError

import config.config
from utils.japanese_utils import is_japanese_lyrics, is_fully_translated, convert_kana
from utils.helpers import sleep_minutes, get_resume_index
from models.conversion_log import ConversionLog
from models.lyrics import Type
from utils.input_utils import prompt_response, prompt_choices
from utils.logger import get_logger
from utils.string_utils import extract_lyrics_kai, extract_japanese_lyrics
from web.mgp import MGPPage, replace_lyrics_jap, save_edit, get_page, fetch_vj_songs
from web.vocaloid_lyrics_wiki import get_romaji


def convert_page_text(page: MGPPage, log: ConversionLog) -> Optional[str]:
    """
    Add furigana to the text of a MGP page
    :param page: The page object
    :param log: Records of event that happened during conversion
    :return: None if failed. A str object representing the new text if successful.
    """
    # extract the indices of {{LyricsKai...}}
    get_logger().debug("Extracting LyricsKai")
    lk = extract_lyrics_kai(page.wikitext)
    if not lk:
        get_logger().warning("Failed to extract LyricsKai from " + str(page))
        return None
    lyrics_kai_start, lyrics_kai_end = lk
    # extract the content of LyricsKai
    lyrics = page.wikitext[lyrics_kai_start:lyrics_kai_end]
    # extract the indices of Japanese lyrics
    get_logger().debug("Extracting Japanese lyrics")
    lj = extract_japanese_lyrics(lyrics)
    if not lj:
        get_logger().warning("Failed to extract |original= from " + str(page))
        return None
    jap_start, jap_end = lj
    # extract the str of the Japanese lyrics
    lyrics_jap = lyrics[jap_start:jap_end]
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
    # add Photrans button and put everything together
    lyrics = "{{Photrans/button|align=;float:right}}" + lyrics[:jap_start] + lyrics_jap + lyrics[jap_end:]
    text = page.wikitext[:lyrics_kai_start] + lyrics + page.wikitext[lyrics_kai_end:]
    return text


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
        return save_edit(text, page, logs)
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
                               "MGP is probably unreachable due to WAF or DDOS. Will try again in 10 minutes.")
            sleep_minutes(10)
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
    choice = prompt_choices("Mode?", ["Manual", "Auto"])
    if choice == 1:
        manual_mode()
        return
    songs: list[str] = fetch_vj_songs()
    # continue from where the bot stopped last time
    index = get_resume_index(songs)
    while index < len(songs):
        # process the current song in the list
        song = songs[index]
        process_song(song)
        # this song has been finished; disallow SIGINT while file io in progress
        signal.signal(signal.SIGINT, signal.SIG_IGN)
        with open("continue.txt", "w") as f:
            f.write(str(song))
            f.flush()
        signal.signal(signal.SIGINT, signal.SIG_DFL)
        index += 1