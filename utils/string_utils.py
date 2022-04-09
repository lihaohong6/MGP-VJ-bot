from typing import Optional, Iterable, Callable, Union


def find_in_string(s: str, lst: list[str]) -> list[int]:
    index = 0
    result = []
    for sub_str in lst:
        index = s.find(sub_str, index)
        if index == -1:
            return result
        result.append(index)
        index += len(sub_str)
    return result


def find_all_matches_in_string(s: str, lst: Iterable[str]) -> list[list[int]]:
    # TODO: hamming distance 1 option
    lst = list(lst)
    result = []

    def find_all_matches_recursive(cur: str, remaining: list[str], prev: list[int], index_add: int):
        if len(remaining) == 0:
            result.append(prev)
            return
        target = remaining[0]
        remaining = remaining[1:]
        while target in cur:
            index = cur.find(target)
            next_list = list(prev)
            next_list.append(index + index_add)
            # FIXME: what if the target is an empty string? infinite recursions
            cur = cur[index + max(len(target), 1):]
            index_add += index + len(target)
            find_all_matches_recursive(cur, remaining, next_list, index_add)

    find_all_matches_recursive(s, lst, [], 0)
    return result


def count_symbol_not_in_bracket(text: str, symbol: Union[str, Callable[[str], bool]], index: int = 0) -> int:
    answer = 0
    while True:
        res = find_symbol_not_in_bracket(text, symbol, index)
        if res == -1:
            return answer
        answer += 1
        index = res + 1


def find_symbol_not_in_bracket(text: str, symbol: Union[str, Callable[[str], bool]], index: int = 0) -> int:
    stack = []
    if isinstance(symbol, str):
        predicate = lambda s: s == symbol
    else:
        predicate = symbol
    while index < len(text) - 1:
        two_chars = text[index: index + 2]
        if two_chars == "{{":
            stack.append(True)
            index += 1
        elif two_chars == "}}":
            if len(stack) > 0:
                stack.pop()
            else:
                return -1
            index += 1
        if predicate(text[index]) and len(stack) == 0:
            return index
        index += 1
    if index == len(text) - 1 and text[index] == symbol:
        return index
    return -1


def find_closing_bracket(text: str, index: int = 0) -> int:
    stack = []
    while index < len(text) - 1:
        two_chars = text[index: index + 2]
        if two_chars == "{{":
            stack.append(True)
        elif two_chars == "}}":
            if len(stack) == 0:
                return index + 2
            stack.pop()
            index += 1
        index += 1
    return len(text)


def extract_lyrics_kai(text: str) -> Optional[tuple[int, int]]:
    """
    Extract the LyricsKai template from text
    :param text: A str object representing the template
    :return: None if LyricsKai is not found. If it is found, return a tuple containing the
    starting index and ending index of the LyricsKai template.
    """
    # FIXME: is lower case lyricsKai also possible?
    index = text.find("{{LyricsKai")
    if index == -1:
        return None
    end = find_closing_bracket(text, index + 2)
    if end == -1:
        return None
    return index, end


def is_empty(s: str) -> bool:
    return s is None or len(s) == 0 or s.isspace()


def extract_japanese_lyrics(text: str) -> Optional[tuple[int, int]]:
    """
    Try to find "original=" in lyrics
    :param text: The content of a LyricsKai template
    :return: Indices of the start and end of Japanese lyrics, if they are found.
    """
    indices = find_in_string(text, ["|", "original", "="])
    if len(indices) < 3:
        return None
    jap_start = indices[2] + 1
    jap_end = find_symbol_not_in_bracket(text, "|", index=jap_start)
    if jap_end == -1:
        jap_end = len(text)
    # try to remove the name of the song
    # for example
    # '''雨き声残響'''
    # 自分より...
    indices = find_in_string(text[jap_start:jap_end], ["'''", "'''"])
    if len(indices) == 2 and is_empty(text[jap_start:jap_start + indices[0]]):
        jap_start = jap_start + indices[1] + 3
    return jap_start, jap_end
