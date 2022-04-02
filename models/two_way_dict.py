class TwoWayDict(dict):
    def __setitem__(self, key, value):
        # Remove any previous connections with these values
        if key in self:
            del self[key]
        if value in self:
            del self[value]
        dict.__setitem__(self, key, value)
        dict.__setitem__(self, value, key)

    def __delitem__(self, key):
        dict.__delitem__(self, self[key])
        dict.__delitem__(self, key)

    def __len__(self):
        """Returns the number of connections"""
        return dict.__len__(self) // 2


hiragana_table = {"a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
                  "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
                  "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
                  "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
                  "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
                  "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
                  "da": "だ", "de": "で", "do": "ど",
                  "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
                  "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
                  "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
                  "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
                  "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
                  "ya": "や", "yu": "ゆ", "yo": "よ",
                  "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
                  "wa": "わ", "wo": "を",
                  "n": "ん",
                  "kya": "きゃ", "kyu": "きゅ", "kyo": "きょ",
                  "gya": "ぎゃ", "gyu": "ぎゅ", "gyo": "ぎょ",
                  "sha": "しゃ", "shu": "しゅ", "sho": "しょ",
                  "ja": "じゃ", "ju": "じゅ", "jo": "じょ",
                  "cha": "ちゃ", "chu": "ちゅ", "cho": "ちょ",
                  "nya": "にゃ", "nyu": "にゅ", "nyo": "にょ",
                  "hya": "ひゃ", "hyu": "ひゅ", "hyo": "ひょ",
                  "bya": "びゃ", "byu": "びゅ", "byo": "びょ",
                  "pya": "ぴゃ", "pyu": "ぴゅ", "pyo": "ぴょ",
                  "mya": "みゃ", "myu": "みゅ", "myo": "みょ",
                  "rya": "りゃ", "ryu": "りゅ", "ryo": "りょ",
                  "vu": "ゔ"}

katakana_dict = {'ア': 'a', 'イ': 'i', 'ウ': 'u', 'ヴ': 'vu', 'ヴァ': 'va', 'ヴィ': 'vi',
                  'ヴェ': 've', 'ヴォ': 'vo', 'エ': 'e', 'オ': 'o', 'カ': 'ka', 'ガ': 'ga', 'キ': 'ki',
                  'キャ': 'kya', 'キュ': 'kyu', 'キョ': 'kyo', 'ギ': 'gi', 'ギャ': 'gya', 'ギュ': 'gyu', 'ギョ': 'gyo', 'ク': 'ku',
                  'グ': 'gu', 'ケ': 'ke', 'ゲ': 'ge', 'コ': 'ko', 'ゴ': 'go', 'サ': 'sa', 'ザ': 'za', 'シ': 'shi', 'シャ': 'sha',
                  'シュ': 'shu', 'ショ': 'sho', 'シェ': 'she', 'ジ': 'ji', 'ジャ': 'ja', 'ジュ': 'ju', 'ジョ': 'jo', 'ス': 'su',
                  'ズ': 'zu', 'セ': 'se', 'ゼ': 'ze', 'ソ': 'so', 'ゾ': 'zo', 'タ': 'ta', 'ダ': 'da', 'チ': 'chi', 'チャ': 'cha',
                  'チュ': 'chu', 'チョ': 'cho', 'ヂ': 'ji', 'ヂャ': 'ja', 'ヂュ': 'ju', 'ヂョ': 'jo', 'ティ': 'ti', 'ツ': 'tsu', 'ヅ': 'zu', 'テ': 'te',
                  'デ': 'de', 'ト': 'to', 'ド': 'do', 'ドゥ': 'du', 'ナ': 'na', 'ニ': 'ni', 'ニャ': 'nya', 'ニュ': 'nyu',
                  'ニョ': 'nyo', 'ヌ': 'nu', 'ネ': 'ne', 'ノ': 'no', 'ハ': 'ha', 'バ': 'ba', 'パ': 'pa', 'ヒ': 'hi', 'ヒャ': 'hya',
                  'ヒュ': 'hyu', 'ヒョ': 'hyo', 'ビ': 'bi', 'ビャ': 'bya', 'ビュ': 'byu', 'ビョ': 'byo', 'ピ': 'pi', 'ピャ': 'pya',
                  'ピュ': 'pyu', 'ピョ': 'pyo', 'フ': 'fu', 'ファ': 'fa', 'フィ': 'fi', 'フェ': 'fe', 'フォ': 'fo', 'フュ': 'fu',
                  'ブ': 'bu', 'プ': 'pu', 'ヘ': 'he', 'ベ': 'be', 'ペ': 'pe', 'ホ': 'ho', 'ボ': 'bo', 'ポ': 'po', 'マ': 'ma',
                  'ミ': 'mi', 'ミャ': 'mya', 'ミュ': 'myu', 'ミョ': 'myo', 'ム': 'mu', 'メ': 'me', 'モ': 'mo', 'ャ': 'xya',
                  'ヤ': 'ya', 'ュ': 'xyu', 'ユ': 'yu', 'ヨ': 'yo', 'ラ': 'ra', 'リ': 'ri', 'リャ': 'rya',
                  'リュ': 'ryu', 'リョ': 'ryo', 'ル': 'ru', 'レ': 're', 'ロ': 'ro', 'ヮ': 'xwa', 'ワ': 'wa', 'ウィ': 'wi',
                  'ヰ': 'wi', 'ヱ': 'we', 'ウェ': 'we', 'ヲ': 'wo', 'ウォ': 'wo', 'ン': "n", 'ディ': 'di',
                  'チェ': 'che', 'ジェ': 'je'}

hiragana_dict = TwoWayDict()

for k in hiragana_table:
    hiragana_dict[k] = hiragana_table[k]
