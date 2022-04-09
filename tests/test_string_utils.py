from unittest import TestCase
from utils.string_utils import *


class Test(TestCase):
    def test_find_in_string(self):
        s = "{{= LyricsKai = "
        self.assertEqual([0, 4, len(s) - 2],
                         find_in_string(s,
                                        ["{{", "LyricsKai", "=", "something"]))

    def test_find_symbol_not_in_bracket(self):
        s1 = "歌词：{{Photrans|私|{{ruby|わたし|???}}}}は\n|translation=something|textcolor=}}"
        self.assertEqual(s1.find("\n") + 1, find_symbol_not_in_bracket(s1, "|"))

    def test_find_closing_bracket(self):
        s1 = "{{Photrans|abc|def}}}}xx"
        self.assertEqual(len(s1) - 2,
                         find_closing_bracket(s1))
        s2 = "{{aoijijos{{ois}}"
        self.assertEqual(len(s2), find_closing_bracket(s2))
        s3 = "zzz{}xxx}} "
        self.assertEqual(len(s3) - 1, find_closing_bracket(s3))

    yscx = """== 歌词 ==
Sometext here.\n{{LyricsKai
|lbgcolor=#000000
|containerstyle=color:#ffffff;
|original=
{{ruby|風|ふう}}が{{photrans|通|とお}}り{{photrans|過|す}}ぎた
{{ruby|未完成|{{photrans|蜜柑星|みかんせい}}}}な
|translated=
???
}}
Some more text here.
}}
"""

    def test_extract_lyrics_kai(self):
        s1 = self.yscx
        self.assertEqual((s1.find(".\n") + 2, s1.find("\nSome more")),
                         extract_lyrics_kai(s1))

    def test_extract_japanese_lyrics(self):
        lk = extract_lyrics_kai(self.yscx)
        lyrics = self.yscx[lk[0]:lk[1]]
        self.assertEqual((lyrics.find("=\n{{") + 1, lyrics.find("な\n|") + 2),
                         extract_japanese_lyrics(lyrics))
        s2 = """{{LyricsKai|lstyle=color:#4E9DDF|rstyle=color:#0F3077
|original=
'''雨き声残響'''
{{photrans|自分|じぶん}}より{{photrans|下手|へた}}くそな{{photrans|人|ひと}}}}"""
        self.assertEqual((s2.rfind("'''") + 3, len(s2)), extract_japanese_lyrics(s2))

    def test_find_all_matches_in_string(self):
        s = "aaa"
        self.assertEqual([[0], [1], [2]], find_all_matches_in_string(s, ['a']))
        self.assertEqual([[0, 1], [0, 2], [1, 2]], find_all_matches_in_string(s, ['a', 'a']))
        s = "abcbcabcdab"
        self.assertEqual([[0, 2], [0, 4], [0, 7], [5, 7]], find_all_matches_in_string(s, ['ab', 'c']))
        print([[2, 12, 20, 29, 34], [2, 12, 23, 29, 34]],
              find_all_matches_in_string("yamanainoameganatsuzoraosemeiniegaitatte",
                                         ["manaino", "ga", "o", "ni", "itatte"]))
