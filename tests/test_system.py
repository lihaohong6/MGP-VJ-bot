from unittest import TestCase

from bots.auto_furigana import convert_page_text
from models.conversion_log import ConversionLog
from web.mgp import MGPPage

class Object(object):
    pass

class SystemsTest(TestCase):
    def test_convert_page_text(self):
        page = Object()
        setattr(page, 'song_names', ["雨き声残響"])
        setattr(page, 'id', '123')
        setattr(page, 'title', '雨声残响')
        setattr(page, 'wikitext', """{{VOCALOID传说曲题头}}
{{VOCALOID_Songbox
|image    = 雨声残响.jpg
|图片信息 = Illustration by 巨大ねこ
|颜色 = #0F3077; color:#FFEF68;
|演唱     = [[IA]]
|歌曲名称 = {{lj|雨き声残響}}<br />雨声残响
|P主      = [[Orangestar]](蜜柑星P)
|nnd_id   = sm24626484
|yt_id    = 0KK5vQlCVYo
|其他资料 = 于2014年10月5日投稿至niconico，再生数为{{NiconicoCount|id=sm24626484}}<br>同日投稿至YouTube，再生数为1,993,000+
}}
{{Cquote|竭力大喊的聲音也會在雨中漸漸消逝。這樣就好了。|Orangestar}}

《'''{{lj|雨き声残響}}'''》是'''Orangestar'''于2014年10月5日投稿至niconico的VOCALOID原创歌曲，其第十五作。

歌词中的【未完成】读音等同于【蜜柑星】，“{{lj|雨き}}”则应该是“{{lj|叫き}}”的变形。

== 歌曲 ==
:;原版
{{BilibiliVideo|id=1594252}}
:;-かましょ Acoustic Arrange-
{{BilibiliVideo|id=2274759|page=1}}
== 歌词 ==
{{LyricsKai|lstyle=color:#4E9DDF|rstyle=color:#0F3077
|original=
'''雨き声残響'''

自分より下手くそな人
探して浸るの優越感
でもその度ちょっと自分を嫌って
次元遡って現実逃避
でも良いんじゃない？
別に良いんじゃない？
無理に強がらなくても良いんじゃない？
下を見て強くなれるのも
また人だからさ。

五月蠅い　もううざい　くらいにCryを掻き消す様な
世界なら　抗ってたいのに
降り出した空の泣き声は透明で
『わかんない、もうわかんないよ！』を何遍も。

僕達は存在証明に　毎日一生懸命で
こんな素晴らしい世界で
まだ生きる意味を探してる
そりゃそうだろだって人間は
希望無しでは生きられないからさ
みんな　心のどっかで 来世を信じてる。

昨日の僕守る為に　笑うくらいなら
泣いたっていいだろ？　ねぇ
止まないの雨が　夏空を鮮明に描いたって
僕達は不完全で

未完成な

|translated='''翻译：小艾伊好'''<ref>https://www.jianshu.com/p/2bcb84601a07</ref>

尋找比自己更沒用的人
沉浸於這般的優越感之中
但每當這樣做就會有點變得討厭自己
回遡次元  逃避現實
但這樣也不錯吧？
就這樣不就好了嗎？
即使不勉強去逞強也可以吧？
向下望就能變得堅強
因為我也不過是人啊

吵死了  真的麻煩死了  如此  將哭泣聲  消抹掉似的
這般的世界  我明明就想要去與之抵抗
降雨的天空的  哭泣聲卻是透明的
我不懂啊  我不管了啊  無數次這樣說道

我們為了存在的證明  每天都拼命過活
在如此美妙的世界
繼續去探求活著的意義
因為說着  那是理所當然的吧  的人們
沒有了希望就活不下去了啊
大家  在心裹某處  都是深信着來世的

若然歡笑  只是為了守護昨天的我
那即使我哭了也沒有關係吧  吶 
不止的雨  即使鮮明地描繪出夏日的天空
我們亦是不完美而

不成熟的呢

}}


{{Orangestar}}

== 注释与外部链接 ==
<references/>

[[分类:日本音乐作品]][[Category:使用VOCALOID的歌曲]][[分类:IA歌曲]]
""")
        logs = ConversionLog()
        res = convert_page_text(page, logs)
        expected = """{{VOCALOID传说曲题头}}
{{VOCALOID_Songbox
|image    = 雨声残响.jpg
|图片信息 = Illustration by 巨大ねこ
|颜色 = #0F3077; color:#FFEF68;
|演唱     = [[IA]]
|歌曲名称 = {{lj|雨き声残響}}<br />雨声残响
|P主      = [[Orangestar]](蜜柑星P)
|nnd_id   = sm24626484
|yt_id    = 0KK5vQlCVYo
|其他资料 = 于2014年10月5日投稿至niconico，再生数为{{NiconicoCount|id=sm24626484}}<br>同日投稿至YouTube，再生数为1,993,000+
}}
{{Cquote|竭力大喊的聲音也會在雨中漸漸消逝。這樣就好了。|Orangestar}}

《'''{{lj|雨き声残響}}'''》是'''Orangestar'''于2014年10月5日投稿至niconico的VOCALOID原创歌曲，其第十五作。

歌词中的【未完成】读音等同于【蜜柑星】，“{{lj|雨き}}”则应该是“{{lj|叫き}}”的变形。

== 歌曲 ==
:;原版
{{BilibiliVideo|id=1594252}}
:;-かましょ Acoustic Arrange-
{{BilibiliVideo|id=2274759|page=1}}
== 歌词 ==

{{photrans/button}}

{{LyricsKai|lstyle=color:#4E9DDF|rstyle=color:#0F3077
|original=
'''雨き声残響'''

{{photrans|自分|じぶん}}より{{photrans|下手|へた}}くそな{{photrans|人|ひと}}
{{photrans|探|さが}}して{{photrans|浸|ひた}}るの{{photrans|優越感|ゆうえつかん}}
でもその{{photrans|度|たび}}ちょっと{{photrans|自分|じぶん}}を{{photrans|嫌|きら}}って
{{photrans|次元|じげん}}{{photrans|遡|さかのぼ}}って{{photrans|現実|げんじつ}}{{photrans|逃避|とうひ}}
でも{{photrans|良|い}}いんじゃない？
{{photrans|別|べつ}}に{{photrans|良|い}}いんじゃない？
{{photrans|無理|むり}}に{{photrans|強|つよ}}がらなくても{{photrans|良|い}}いんじゃない？
{{photrans|下|した}}を{{photrans|見|み}}て{{photrans|強|つよ}}くなれるのも
また{{photrans|人|ひと}}だからさ。

{{photrans|五月蠅|うるさ}}い　もううざい　くらいにCryを{{photrans|掻|か}}き{{photrans|消|け}}す{{photrans|様|よう}}な
{{photrans|世界|せかい}}なら　{{photrans|抗|あらが}}ってたいのに
{{photrans|降|ふ}}り{{photrans|出|だ}}した{{photrans|空|そら}}の{{photrans|泣|な}}き{{photrans|声|ごえ}}は{{photrans|透明|とうめい}}で
『わかんない、もうわかんないよ！』を{{photrans|何遍|なんべん}}も。

{{photrans|僕|ぼく}}{{photrans|達|たち}}は{{photrans|存在|そんざい}}{{photrans|証明|しょうめい}}に　{{photrans|毎日|まいにち}}{{photrans|一生懸命|いっしょうけんめい}}で
こんな{{photrans|素晴|すば}}らしい{{photrans|世界|せかい}}で
まだ{{photrans|生|い}}きる{{photrans|意味|いみ}}を{{photrans|探|さが}}してる
そりゃそうだろだって{{photrans|人間|にんげん}}は
{{photrans|希望|きぼう}}{{photrans|無|な}}しでは{{photrans|生|い}}きられないからさ
みんな　{{photrans|心|こころ}}のどっかで {{photrans|来世|らいせ}}を{{photrans|信|しん}}じてる。

{{photrans|昨日|きのう}}の{{photrans|僕|ぼく}}{{photrans|守|まも}}る{{photrans|為|ため}}に　{{photrans|笑|わら}}うくらいなら
{{photrans|泣|な}}いたっていいだろ？　ねぇ
{{photrans|止|や}}まないの{{photrans|雨|あめ}}が　{{photrans|夏空|なつそら}}を{{photrans|鮮明|せんめい}}に{{photrans|描|えが}}いたって
{{photrans|僕|ぼく}}{{photrans|達|たち}}は{{photrans|不完全|ふかんぜん}}で

{{photrans|未完成|みかんせい}}な

|translated='''翻译：小艾伊好'''<ref>https://www.jianshu.com/p/2bcb84601a07</ref>

尋找比自己更沒用的人
沉浸於這般的優越感之中
但每當這樣做就會有點變得討厭自己
回遡次元  逃避現實
但這樣也不錯吧？
就這樣不就好了嗎？
即使不勉強去逞強也可以吧？
向下望就能變得堅強
因為我也不過是人啊

吵死了  真的麻煩死了  如此  將哭泣聲  消抹掉似的
這般的世界  我明明就想要去與之抵抗
降雨的天空的  哭泣聲卻是透明的
我不懂啊  我不管了啊  無數次這樣說道

我們為了存在的證明  每天都拼命過活
在如此美妙的世界
繼續去探求活著的意義
因為說着  那是理所當然的吧  的人們
沒有了希望就活不下去了啊
大家  在心裹某處  都是深信着來世的

若然歡笑  只是為了守護昨天的我
那即使我哭了也沒有關係吧  吶 
不止的雨  即使鮮明地描繪出夏日的天空
我們亦是不完美而

不成熟的呢

}}


{{Orangestar}}

== 注释与外部链接 ==
<references/>

[[分类:日本音乐作品]][[Category:使用VOCALOID的歌曲]][[分类:IA歌曲]]
"""
        print(logs)
        self.assertEqual(expected, res)

    def test_convert_page_text2(self):
        page = MGPPage(["星命学"], canonical_title="星命学", id="507401", text="""{{LyricsKai
|containerstyle=background:#EDEDED
|original =
いつの日か　貴方が死んだなら
星の命に身体を委ねて
夢香る季節に探すだろう
再会の言葉を飾った
あの花を

結んで　開いて　創り上げたのは
地球の息の根　止める兵器たち
結んだ　左手　絡まるくらいに
貴方を掴んだ

どれだけ　涙で濡らしても
咲くことのない　花の種を蒔く

誰かに　奪われた人生の後先に
還るべき星が有りますように
今　一瞬を抱きしめて
愛を伝えられるのなら
それだけで幸せなのに

遠い未来の　話をしようよ
語り合い過ぎて　日が暮れる程の
毎日が欲しいんだ

神様　何処で何をしてるの？
ちょっとはこっちの話聞いてよ
叶わぬことを望む

確かに　繋がれた人生の後先に
守るべき星が有りますように
今　運命と見つめ合って
愛に応えられるのなら
それだけで幸せだ

夜を知って　朝に泣いた
触れた身体　冷たかった
碧く澄んだその瞳は
まだ変わらぬまま
貴方だけを　貴方だけを
貴方だけを　貴方だけを
貴方だけは　まだ

涙に　刻まれた幾千もの後悔は
この歌と共に捨てていくから
きっと　いつの日かこの場所で
二人で笑い合える　時が来る

誰かに　奪われた人生の後先に
還るべき星が有りますように
今　一瞬を抱きしめて
愛を伝えられるのなら
それだけで幸せだ
それだけで幸せだ
それだけが幸せだ
|translated=
如果总有一天　你会死去的话
就将躯体交给星命吧
在散发着美梦香气的季节中找找看吧
粉饰了那再会的话语
将那朵花

攥紧　再松开　创造出来的是
将地球的生命　扼杀的兵器
攥紧了的　左手　似是缠绕在一起一般
紧紧抓住你

将即便被多少眼泪打湿
也不会盛开的　花的种子播下

在被谁　所夺去的人生的前前后后
像是有着必须归还的星星那样
现在　拥抱着那一瞬间
如果能将爱传达出去的话
只是那样的话就已经很幸福了

说些　关于遥远未来的话吧
聊得又太久了　久得天色都已经暗沉下去
每天都在渴望着啊

神大人啊　在哪里在做什么呢？
稍微听听这边的人说话吧
期望着无法实现的事情

在确实地　被连结在一起的人生的前前后后
像是有着必须守护的星星那样
现在　与命运视线相接
如果能对爱做出回应的话
只是那样的话就已经是幸福了

知晓了夜晚　在早晨哭泣
被触碰的身体　已经变得冰冷
湛蓝而清澈的那双眼睛
仍没有改变
仅仅将你　仅仅将你
仅仅将你　仅仅将你
因为只有你　仍未

在泪水中　刻下的成千上万的后悔
与这首歌一起舍弃掉
在这个地方
两人能相对而笑的时候　总有一天会到来

在被谁　所夺去的人生的前前后后
像是有着必须归还的星星那样
现在　拥抱着那一瞬间
如果能将爱传达出去的话
只是那样的话就已经是幸福了
只是那样的话就已经是幸福了
只是那样的话就已经是幸福了​
}}
""")
        logs = []
        actual = convert_page_text(page, logs)
        print(actual)
        print(logs)

