from dataclasses import dataclass, field

from models.lyrics import Word


ConversionList = list[tuple[Word, Word]]


@dataclass
class ConversionLog:
    word_conversions: ConversionList = field(default_factory=list)
    used_conversions: ConversionList = field(default_factory=list)
    invalid_conversions: ConversionList = field(default_factory=list)
    removed_conversions: ConversionList = field(default_factory=list)
    all_words: list[Word] = field(default_factory=list)

    def word_used(self, word: Word):
        self.all_words.append(word)
        for w in self.word_conversions:
            if w[1].surface == word.surface and w[1].hiragana == word.hiragana:
                self.used_conversions.append(w)
                return
