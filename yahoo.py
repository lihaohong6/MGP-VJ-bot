import json
import logging
from dataclasses import dataclass
from typing import Optional

import pykakasi
import requests

from utils.caching import get_cache, save_cache
from utils.japanese_char import is_kanji, is_japanese
from models.lyrics import Word, Type


def get_furigana(text: str, page_id: str) -> Optional[list[Word]]:
    cache_filename = "Yahoo" + page_id + ".json"
    response = get_cache(cache_filename)
    if response is None or page_id == "0":
        text = ''.join(c for c in text
                       if is_japanese(c) or c == "\n" or c == " " or c == "　")
        url = "https://api.nzh21.site/yahooapis/FuriganaService/V2/furigana"
        header = {
            'x-ua': "Yahoo AppID: dj00aiZpPXE2azZNYXFyR29kSSZzPWNvbnN1bWVyc2VjcmV0Jng9ODY-"
        }
        r = {
            "id": "1234-1",
            "jsonrpc": "2.0",
            "method": "jlp.furiganaservice.furigana",
            "params": {
                "q": text,
                "grade": 1
            },
            "appid": "dj00aiZpPXE2azZNYXFyR29kSSZzPWNvbnN1bWVyc2VjcmV0Jng9ODY-"
        }
        s = json.dumps(r)
        response = requests.post(url, headers=header, data=s).text
        save_cache(cache_filename, response)
    response = json.loads(response)
    if 'result' not in response:
        return None
    response = response['result']['word']
    result = []
    for r in response:
        if 'subword' in r:
            words = r['subword']
        else:
            words = [r]
        for word in words:
            surface: str = word['surface']
            if surface.isspace():
                continue
            if is_kanji(surface[0]):
                # does not create furigana for "千" in "涙に 刻まれた幾千もの後悔は"
                if 'furigana' in word:
                    furigana = word['furigana']
                else:
                    kks = pykakasi.Kakasi()
                    furigana = "".join([word['hira'] for word in kks.convert(surface)])
                    logging.warning("Yahoo does not provide furigana for " + surface + ". " +
                                    "Using " + furigana + " from pykakasi as fallback.")
                result.append(Word(surface=surface, type=Type.KANJI,
                                   hiragana=furigana))
            else:
                result.append(Word(surface=surface, type=Type.KANA))
    return result
