# MGP-VJ-bot 萌娘百科VJ机器人

This project has limited documentation.

文档很少，将就着看吧。

## Intro

Creates furigana based on [Yahoo's api](https://developer.yahoo.co.jp/webapi/jlp/furigana/v2/furigana.html) and a romaji transliteration. 

Made for Moegirlpedia, but can be adapted to other use cases. 

## Usage Help
1. Install required dependencies in `requirements.txt`. 
2. Create file "user-password.py" according to the [manual of pywikibot](https://www.mediawiki.org/wiki/Manual:Pywikibot/BotPasswords). 
3. Run main.py and input 1 for manual mode
4. Input name of the page
5. The program may prompt for manual intervention. If so, input the corresponding option.
6. The program may either push the change automatically (if everything goes smoothly) or ask for manual confirmation if suspicious changes are made. 
7. Repeat 4 to 6 for more pages.

Note that auto mode will automatically create a list of all VJ songs and go through them one by one.

## How it works

For example, given these as input
>夏空を鮮明に

>natsuzoraosenmeini

The program converts kana to romaji

1. を becomes `['o', 'wo']` (both are valid transliterations)
2. に becomes `['ni']`

It now searches in the romaji of Vocaloid Lyrics Wiki and match the remaining unmatched Kanji with the romaji. Thus, we have two possibilites

1. 夏空 => natsuz; 鮮明 => raosenmei
2. 夏空 => natsuzora; 鮮明 => senmei

Clearly, 1 is wrong and 2 is correct. 1 is listed as a possibility because を can be matched with either the first 'o' in 'zo' or the second 'o'. 

The program employs multiple measures to determine which one is correct. For example, "natsuz" cannot be converted to hiragana since the "z" is inconvertible. Furthermore, Yahoo might have already determined that 鮮明 is "senmei". Correcting "seimei" with "raoseimei", which is not a valid pronunciation, will also decrease the likelihood that this conversion is correct.

Among all possible combinations, the program chooses the one most likely to be correct. 
