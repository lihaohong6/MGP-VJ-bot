from dataclasses import dataclass, field
from enum import Enum


class Type(Enum):
    KANA = 0,
    ENGLISH = 1,
    KANJI = 2


@dataclass
class Word:
    surface: str
    type: Type
    romaji: list[str] = field(default_factory=list)
    hiragana: str = ""

    def __eq__(self, other):
        return self.surface == other.surface and \
               self.type == other.type and \
               self.hiragana == other.hiragana

    def __hash__(self):
        return hash((self.surface, self.type.value, self.hiragana))
