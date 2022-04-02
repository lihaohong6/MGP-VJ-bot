import itertools
import logging
from typing import Optional, Union

import config.config
import yahoo
from models.conversion_log import ConversionLog, ConversionList
from models.lyrics import Word, Type
from string_utils import find_all_matches_in_string, find_symbol_not_in_bracket, is_empty, count_symbol_not_in_bracket
from utils.japanese_char import is_kana, is_kanji, is_japanese, get_pronunciations, romaji_to_hiragana, kana_to_romaji


def is_japanese_lyrics(lyrics: str) -> bool:
    # there must exist at least 1 kana character and at least 1 kanji character
    return any([is_kana(c) for c in lyrics]) and \
           any([is_kanji(c) for c in lyrics])


def is_fully_translated(lyrics: str) -> bool:
    """
    Check whether Japanese lyrics is fully translated
    :param lyrics: Lyrics text
    :return: True if translated. False otherwise.
    """
    # count number of kanji
    kanji_count = len([c for c in lyrics if is_kanji(c)])
    # count number of kanji not in a template
    no_furigana_count = count_symbol_not_in_bracket(lyrics, is_kanji)
    return kanji_count == 0 or no_furigana_count / kanji_count < 0.5


def lyrics_match(l1: str, l2: str) -> bool:
    total = 0
    mismatch = 0
    mismatch_list = []
    for c in l1:
        if is_kanji(c):
            total += 1
            if c not in l2:
                mismatch += 1
                mismatch_list.append(c)
    if mismatch == 0:
        return True
    if mismatch / total < 0.1:
        logging.warning("Mismatches between Japanese lyrics: " + str(mismatch_list))
    return False


def join_kana(kana: list[Word]) -> Word:
    s = "".join([k.surface for k in kana])
    return Word(surface=s, type=Type.KANA, hiragana=s)


def jap_line_to_words(jap: str, existing: list[Word]) -> list[Word]:
    """
    Convert a line of Japanese lyrics to a list of conversions
    :param jap: Original japanese without special characters
    :param existing: Existing list of conversions provided by Yahoo's furigana tool
    :return: List of conversions including English ones
    """
    index = 0
    words = []
    jap = "".join([c for c in jap if c != ' ' and c != '　' and c != ''])
    while index < len(jap):
        if len(existing) == 0:
            break
        if existing[0].surface not in jap[index:]:
            rest = jap[index:]
            if is_japanese_lyrics(rest):
                raise AssertionError("Word list dose not match jap")
            words.append(Word(rest, type=Type.ENGLISH))
            break
        location = jap.find(existing[0].surface, index)
        if location == index:
            words.append(existing.pop(0))
            index += len(words[-1].surface)
        else:
            start = index
            while index < len(jap) and not is_japanese(jap[index]):
                index += 1
            words.append(Word(surface=jap[start:index], type=Type.ENGLISH))
    # merge kana such as っ and て together
    prev = list()
    result = []
    for word in words:
        if word.type == Type.KANA:
            prev.append(word)
        else:
            if len(prev) > 0:
                result.append(join_kana(prev))
                prev = []
            result.append(word)
    if len(prev) > 0:
        result.append(join_kana(prev))
    return result


def match_non_kana_with_romaji(word_list: list[Word], romaji: str) -> (int, list[Word]):
    """
    Try to match non-kana characters (english conversions and kanji) with their corresponding romaji.
    :param word_list: List of conversions that are of Type ENGLISH and KANJI
    :param romaji: Corresponding romaji
    :return: A tuple consisting a number that represents the rating of this matching and the
    resulting list of conversions. The higher the rating, the higher the chance that this matching
    is correct.
    """
    MATCHING_KANA = -10
    NON_MATCHING_KANA = -100
    INVALID_RATING_CHANGE = -1000
    # for Kanji, try their supposed kana first
    # for English word, try the unmodified original first
    # if fail, use romaji and decrease rating
    if len(word_list) == 1:
        elem = word_list[0]
        if romaji in elem.romaji:
            return 0, word_list
        else:
            hiragana = romaji_to_hiragana(romaji, report_error=False)
            if hiragana is None:
                rating = INVALID_RATING_CHANGE
            elif hiragana in get_pronunciations(elem.surface):
                rating = MATCHING_KANA
            else:
                rating = NON_MATCHING_KANA
            return rating, [Word(elem.surface, type=elem.type, romaji=[romaji],
                                 hiragana=hiragana)]

    candidates: list[tuple[int, list[Word]]] = []

    def match_recursive(words: list[Word], roma: str, current: tuple[int, list[Word]]):
        if len(words) == 0:
            if len(roma) > 0:
                return
            candidates.append(current)
        if len(roma) == 0:
            return
        cur = words[0]
        for r in cur.romaji:
            if roma.find(r) == 0:
                next_list = (current[0], list(current[1]))
                next_list[1].append(cur)
                return match_recursive(words[1:], roma[len(r):], next_list)
        for index in range(len(cur.surface), len(roma) + 1):
            # FIXME: if matching for English, relax requirements and just get the romaji in there
            hiragana = romaji_to_hiragana(roma[:index])
            if not hiragana:
                continue
            rating = MATCHING_KANA if hiragana in get_pronunciations(cur.surface) else NON_MATCHING_KANA
            next_list = (current[0] + rating, list(current[1]))
            next_list[1].append(Word(cur.surface, cur.type,
                                     romaji=[roma[:index]], hiragana=hiragana))
            match_recursive(words[1:], roma[index:], next_list)
        return

    match_recursive(word_list, romaji, (0, []))
    if len(candidates) == 0:
        return None
    return sorted(candidates, key=lambda p: p[0])[-1]


def convert_kana_line(jap: list[Word], romaji: str) -> Optional[list[Word]]:
    """
    Match a list of words with the expected romaji
    :param jap: A list of Japanese words
    :param romaji: the romaji matching jap
    :return: A list of words with corrected pronunciation if conversion is successful.
    """
    # FIXME: include pronunciation for numbers
    if len(jap) == 0:
        return []
    if len(romaji) == 0:
        return []
    # records possible romaji combinations
    romaji_list_list = []
    # convert existing kana to romaji
    for word in jap:
        if word.type == Type.KANA:
            word.romaji = kana_to_romaji(word.surface)
            romaji_list_list.append(word.romaji)
        elif word.type == Type.KANJI:
            word.romaji = kana_to_romaji(word.hiragana)
        else:
            word.romaji = [word.surface.lower()]
    results = []
    # this is the cartesian product of possible romaji combinations
    # for example, 夏空を鮮明に will become
    # [['o', 'wo'], ['ni']]
    # because を has two transliterations
    # itertools.product converts it to
    # [['o'], ['ni'],
    # ['wo'], ['ni']]
    # the program tries each combination, and will figure out which
    # one has the highest rating
    for romaji_list in itertools.product(*romaji_list_list):
        # remove empty ones from the list
        romaji_list = [s for s in romaji_list if not is_empty(s)]
        # find all possible ways the romaji from kana can match
        # the known romaji
        matches = find_all_matches_in_string(romaji, romaji_list)
        for match in matches:
            res = match_kanji_with_romaji(jap, match, romaji, romaji_list)
            if res is not None:
                results.append(res)
    if len(results) == 0:
        return None
    return sorted(results, key=lambda t: t[0])[-1][1]


def match_kanji_with_romaji(jap: list[Word], match: list[int],
                            romaji: str, romaji_list: list[str]) -> Optional[tuple[int, list[Word]]]:
    """
    Match a list of Japanese words with romaji
    :param jap: List of Japanese words
    :param match: List of known matches between kana and romaji
    :param romaji: romaji string
    :param romaji_list: list of known romaji
    :return: The rating of the resulting matching, and the corrected list of words
    """
    word_index = 0
    romaji_index = 0
    result = []
    rating_sum = 0
    for index in range(len(match)):
        unmatched = []
        # find a sequence of unmatched kanji/english
        while jap[word_index].type != Type.KANA:
            unmatched.append(jap[word_index])
            word_index += 1
        # check if unmatched kanji exist
        if len(unmatched) != 0:
            # try to perform a guess
            res = match_non_kana_with_romaji(
                jap[word_index - len(unmatched):word_index],
                romaji[romaji_index:match[index]])
            if not res:
                return None
            # add the change in rating ot the overall rating
            rating, words = res
            rating_sum += rating
            result.extend(words)
        # add unmodified kana to result
        romaji_index = match[index] + len(romaji_list[index])
        result.append(jap[word_index])
        word_index += 1
    # check if the line ends with kanji
    if word_index < len(jap):
        res = match_non_kana_with_romaji(jap[word_index:], romaji[romaji_index:])
        if not res:
            return None
        rating, words = res
        rating_sum += rating
        result.extend(words)
    return rating_sum, result


def remove_special_characters(s: str) -> str:
    res = []
    for c in s:
        if is_japanese(c) or c.isalnum() or c == ' ':
            res.append(c)
        else:
            res.append(" ")
    return "".join(res)


def log_diff(before: list[Word], after: list[Word], logs: ConversionLog):
    """
    Record the corrections made to Yahoo's furigana tool in logs
    :param before: conversions made by Yahoo
    :param after: corrected conversions based on Vocaloid Lyrics Wiki; parallel list of before
    :param logs: stores conversion records
    :return: None
    """
    before = [w for w in before if w.type == Type.KANJI]
    after = [w for w in after if w.type == Type.KANJI]
    if len(before) != len(after):
        raise Exception("Lengths of kanji list differ in the same line!" + str(before) + str(after))
    for w1, w2 in zip(before, after):
        if w1.surface == w2.surface and w1.hiragana != w2.hiragana:
            logs.word_conversions.append((w1, w2))


def convert_kana(jap: list[str], romaji: list[str], logs: ConversionLog, page_id: str = "0") -> Optional[list[Word]]:
    """
    Convert kanji in Japanese to kana
    :param jap: Japanese lyrics stored in a list. Each element is a line.
    :param romaji: Romaji stored in a list. This is a parallel list with jap.
    :param logs: Store events happen during conversion.
    :param page_id: Id of the page. Not used.
    :return: A list of Word objects each storing the original kanji and the corresponding furigana.
    """
    result: list[Word] = []
    jap = [remove_special_characters(line) for line in jap]
    # query everything at once to avoid exceeding the API usage count of Yahoo
    # this will give a preliminary furigana
    word_list = yahoo.get_furigana("\n".join(jap), page_id)
    if not word_list:
        logging.debug("No Yahoo furigana returned")
        return None
    # process line by line
    for index, j in enumerate(jap):
        # convert this line into separate parts
        # kanji, kana, and english characters are stored separately
        words = jap_line_to_words(j, word_list)
        # match the list of words to the expected romaji for this line
        line = convert_kana_line(words, romaji[index])
        if line is None:
            logging.warning("Line {} cannot be matched with {}.".format(j, romaji[index]))
            # if strict, then fail immediately
            if config.config.line_strict:
                return None
            else:
                line = words
        log_diff(words, line, logs)
        # add this line to result
        result.extend(line)
    return result


def is_invalid_furigana(word: Word) -> bool:
    return word.hiragana not in get_pronunciations(word.surface)


def get_invalid_furigana(words: Union[list[Word], ConversionList]) -> Union[list[Word], ConversionList]:
    if len(words) > 0 and isinstance(words[0], Word):
        return [w for w in words
                if is_invalid_furigana(w)]
    return [(before, after)
            for before, after in words
            if after.hiragana not in get_pronunciations(after.surface)]
