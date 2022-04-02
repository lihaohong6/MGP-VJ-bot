import os

import pywikibot
from jamdict import Jamdict
from pywikibot import APISite

from main import manual_mode, fetch_vj_songs
from mgp import get_vocaloid_japan_pages, MGPPage
from utils import login
from utils.japanese_char import get_pronunciations, romaji_to_hiragana
from vocaloid_lyrics_wiki import retrieve_lyrics_from_page

url = "https://vocaloidlyrics.fandom.com/wiki/%E3%83%AC%E3%82%BE%E3%83%B3%E3%83%87%E3%83%BC%E3%83%88%E3%83%AB%E3%81%AE%E8%8A%B1_(Raison_D%27etre_no_Hana)"

# 素気:すげ=>そっけ
retrieve_lyrics_from_page(url)
# manual_mode()
