import itertools
import logging
import re
from typing import Optional

import jamdict
import pykakasi
from jamdict import Jamdict

from models.two_way_dict import hiragana_dict, katakana_dict

jam = Jamdict()
cursor = jam.kd2.ctx()
kks = pykakasi.Kakasi()
hiragana_pattern = re.compile("[\u3041-\u3096]")
katakana_pattern = re.compile("[\u30A0-\u30FF]")
kanji_pattern = re.compile("[\u3400-\u4DB5\u4E00-\u9FCB\uF900-\uFA6A]")
punctuation_pattern = re.compile("[\uFF5F-\uFF9F]")


def is_hiragana(c: str) -> bool:
    return not not hiragana_pattern.fullmatch(c)


def is_katakana(c: str) -> bool:
    # FIXME: is this the right place to deal with the dot?
    return katakana_pattern.fullmatch(c) is not None and c != '・'


def is_kana(c: str) -> bool:
    return is_hiragana(c) or is_katakana(c)


def is_kanji(c: str) -> bool:
    return c == "々" or not not kanji_pattern.fullmatch(c)


def is_punctuation_or_half_width_katakana(c: str) -> bool:
    return not not punctuation_pattern.fullmatch(c)


def is_english_punctuation(c: str) -> bool:
    return re.fullmatch("[,./'?]", c) is not None


def is_japanese(c: str) -> bool:
    return any([is_kana(c),
                is_kanji(c),
                is_punctuation_or_half_width_katakana(c)])


def process_pronunciation(s: str) -> str:
    if s[0] == '-':
        s = s[1:]
    if s[-1] == '-':
        s = s[:-1]
    if '.' in s:
        s = s[:s.find('.')]
    return s


def get_pronunciations(s: str) -> list[str]:
    possibilities = []
    for c in s:
        res = cursor.select("SELECT ID FROM character WHERE literal='{}'".format(c))
        if len(res) == 0:
            possibilities = []
            break
        char_id = res[0][0]
        res = cursor.select("SELECT ID FROM rm_group WHERE cid={}".format(char_id))
        rm_group_id = res[0][0]
        res = cursor.select("SELECT value FROM reading WHERE gid={} "
                            "AND (r_type='ja_on' OR r_type='ja_kun')".format(rm_group_id))
        text = ["".join([i['hira'] for i in kks.convert(process_pronunciation(r[0]))])
                for r in res]
        possibilities.append(text)
    result: list[str] = []
    for prod in itertools.product(*possibilities):
        result.append("".join(prod))
    res = jam.lookup(s).to_dict()
    for entry in res['entries']:
        for kana in entry['kana']:
            result.append(kana['text'])
    # FIXME: should contain more possibilities such as names
    return list(set(result))


vowels = ['a', 'e', 'i', 'o', 'u']


def romaji_to_hiragana(romaji: str, report_error: bool = False) -> Optional[str]:
    try:
        curr = ""
        result = []
        for i in range(len(romaji)):
            if romaji[i] in vowels:
                curr += romaji[i]
                if curr[0] == 'n' and curr not in hiragana_dict:
                    result.append('ん')
                    curr = curr[1:]
                if len(curr) == 3 and curr[0] == curr[1]:
                    result.append("っ")
                    curr = curr[1:]
                # doo -> どう
                if romaji[i] == 'o' and i > 0 and romaji[i-1] == 'o':
                    result.append("う")
                else:
                    result.append(hiragana_dict.get(curr))
                curr = ""
            else:
                curr += romaji[i]
        if len(curr) > 0:
            result.append(hiragana_dict[curr])
        return "".join(result)
    except Exception as e:
        if report_error:
            logging.error("Cannot convert " + romaji + " to hiragana.")
        return None


def char_to_romaji(kana: str) -> list[str]:
    special = {
        'へ': ['he', 'e'],
        'ヲ': ['wo', 'o'],
        'を': ['wo', 'o'],
        'は': ['ha', 'wa'],
        'ふ': ['fu', 'hu'],
        'フ': ['fu', 'hu'],
        'づ': ['zu'],
        'ぢ': ['ji'],
        'ぁ': ['a'],
        'ぃ': ['i'],
        'ぅ': ['u'],
        'ぇ': ['e'],
        'ぉ': ['o']
    }
    if kana in special:
        return special[kana]
    if kana in hiragana_dict:
        return [hiragana_dict[kana]]
    if kana in katakana_dict:
        return [katakana_dict[kana]]
    logging.warning("Failed to convert " + kana + " to romaji.")
    return [kana]


def kana_to_romaji(kana_original: str) -> list[str]:
    # FIXME: だっ -> da? where ? is the wildcard character
    # FIXME: 一致(いっち) is transcribed as itchi
    def recursive_to_romaji(kana: str) -> list[list[str]]:
        if len(kana) == 0:
            return []
        if 'っ' in kana or 'ッ' in kana:
            index = max(kana.find('っ'), kana.find('ッ'))
            before = recursive_to_romaji(kana[:index])
            after = recursive_to_romaji(kana[index + 1:])
            options = ['h', '']
            if len(after) > 0:
                options.append(after[0][0][0])
            if len(before) > 0:
                options.append(before[-1][0][-1])
            return before + [options] + after
        if 'ー' in kana:
            index = kana.find("ー")
            front = recursive_to_romaji(kana[:index])
            back = recursive_to_romaji(kana[index + 1:])
            # FIXME: use wildcard
            pronunciation = front[-1][0][-1] if len(front) > 0 else ""
            return front + [[pronunciation]] + back
        if len(kana) >= 2 and kana[:2] in hiragana_dict or kana[:2] in katakana_dict:
            return [char_to_romaji(kana[:2])] + recursive_to_romaji(kana[2:])
        return [char_to_romaji(kana[0])] + recursive_to_romaji(kana[1:])

    res = recursive_to_romaji(kana_original)
    return list(set(["".join(elem)
                     for elem in itertools.product(*res)]))
