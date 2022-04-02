from unittest import TestCase
from japanese_utils import *
from utils.japanese_char import romaji_to_hiragana


class Test(TestCase):
    def test_is_japanese_lyrics(self):
        self.assertTrue(is_japanese_lyrics("{{photrans|自分|じぶん}}より{{photrans|下手|へた}}くそな{{photrans|人|ひと}}"))
        self.assertFalse(is_japanese_lyrics("わたし"))
        self.assertFalse(is_japanese_lyrics("啊啊啊，只有中文呢"))

    def test_hiragana_to_romaji(self):
        pass

    def test_convert_kana_line(self):
        words = [Word(surface="でも", type=Type.KANA),
                 Word(surface="良", type=Type.KANJI, hiragana="よ"),
                 Word(surface="いんじゃない", type=Type.KANA)
                 ]
        romaji = "demoiinjanai"
        print(convert_kana_line(words, romaji))

    def test_romaji_to_hiragana(self):
        self.assertEqual("じぶん", romaji_to_hiragana("jibun"))
        self.assertEqual("なに", romaji_to_hiragana("nani"))
        self.assertEqual("なんですか", romaji_to_hiragana("nandesuka"))
        self.assertEqual("きょうわ", romaji_to_hiragana("kyouwa"))

    def test_match_non_kana_with_romaji(self):
        romaji = 'hitosaga'
        words = [Word(surface='人', type=Type.KANJI, romaji=['hito'], hiragana='ひと'),
                 Word(surface='探', type=Type.KANJI, romaji=['saga'], hiragana='さが')]
        self.assertEqual((0, words), match_non_kana_with_romaji(words, romaji))
        romaji = "sa"
        words = [Word(surface='人', type=Type.KANJI, romaji=['hito'], hiragana='ひと')]
        res = match_non_kana_with_romaji(words, romaji)
        words[0].romaji = "sa"
        words[0].hiragana = "さ"
        self.assertEqual((-10, words), res)
        romaji = "dattehito"
        words = [Word(surface='探', type=Type.KANJI, romaji=['saga'], hiragana='さが'),
                 Word(surface='人', type=Type.KANJI, romaji=['hito'], hiragana='ひと')]
        res = match_non_kana_with_romaji(words, romaji)
        words[0].romaji = "datte"
        words[0].hiragana = "だって"
        self.assertEqual((-10, words), res)
        romaji = 'hanakasumi'
        words = [Word(surface='花', type=Type.KANJI, romaji=['hana'], hiragana='はな'),
                 Word(surface='霞', type=Type.KANJI, romaji=['gasumi'], hiragana='がすみ')]
        res = match_non_kana_with_romaji(words, romaji)
        words[1].romaji = "kasumi"
        words[1].hiragana = "かすみ"
        self.assertEqual((-10, words), res)

    def test_jap_line_to_words(self):
        s = "五月蠅い　もううざい　くらいにCryを掻き消す様な"
        kanji = ["五月蠅", "い", "もうう", "ざい", "くらいに", *list("を掻き消す様な")]
        words = [Word(k, type=Type.KANJI) for k in kanji]
        jap_line_to_words(s, words)
        self.assertEqual(0, len(words))

    def test_is_fully_translated(self):
        true_list = ["{{PhoTrans|自分|じぶん}}より",
                     "歌名\n{{photrans|啊|b}}ダダダダダ\n{{ruby|好|す}}きていて\n{{photrans|悲|かな}}し",
                     "{{ruby|abc|def}}"]
        false_list = ["啊这{{ruby|嗯|え}}?", "尋找比自己更沒用的人"]
        for t in true_list:
            self.assertTrue(is_fully_translated(t))
        for f in false_list:
            self.assertFalse(is_fully_translated(f))
