from unittest import TestCase

import wikitextparser
from wikitextparser import Template

from bots.youtube_fallback import update_yt_count, add_youtube_count, convert_views, find_youtube_count
from web.youtube import get_yt_views


class Test(TestCase):
    def test_convert_views(self):
        self.assertEqual(123456, convert_views(123456, "123,456+"))
        self.assertEqual(None, convert_views(123456, "123456"))
        self.assertEqual(None, convert_views(123460, "123456"))
        self.assertEqual(123456, convert_views(123456, "100000"))

    def test_update_yt_count(self):
        yt_id = "Gexhf83mq3M"
        t = Template("{{{{YoutubeCount|id={}|fallback=10}}}}".format(yt_id))
        update_yt_count(t, "A")
        views = get_yt_views(yt_id)
        self.assertEqual(t.string, "{{{{YoutubeCount|id={}|fallback={}}}}}".format(yt_id, views))
        t = Template("{{{{YoutubeCount|id={}}}}}".format(yt_id))
        update_yt_count(t, "A")
        self.assertEqual(t.string, "{{{{YoutubeCount|id={}|fallback={}}}}}".format(yt_id, views))

        # note: this is hard-coded and is intended to ensure that the program does not make small updates
        yt_id = "0KK5vQlCVYo"
        t = Template("{{{{YoutubeCount|id={}|fallback=2951470}}}}".format(yt_id))
        update_yt_count(t, "A")
        self.assertEqual(t.string, "{{{{YoutubeCount|id={}|fallback=2951470}}}}".format(yt_id))

    def test_add_youtube_count(self):
        yt_id = "Gexhf83mq3M"
        wikitext = """{{VOCALOID_Songbox
|yt_id = Gexhf83mq3M
|其他资料 = 于同日投稿至YouTube，再生数为21,3,,92+<br/>于}}"""
        expected = f"""{{{{VOCALOID_Songbox
|yt_id = Gexhf83mq3M
|其他资料 = 于同日投稿至YouTube，再生数为{{{{YoutubeCount|id=Gexhf83mq3M}}}}<br/>于}}}}"""
        t = Template(wikitext)
        add_youtube_count(t, "")
        self.assertEqual(expected, t.string)

    def test_find_youtube_count(self):
        text = "于2015年6月25日投稿至niconico、YouTube<br/>" \
               "再生数分别为{{NiconicoCount|id=sm26567316}}、129,478+<br/>" \
               "次日投稿至bilibili，再生数为{{bilibiliCount|id=BV1ms411U7qS}}"
        s, e = find_youtube_count(text)
        self.assertEqual("129,478+", text[s:e])
        text = "于2017年1月8日投稿至niconico，再生数为 17756（最终记录）<br>" \
               "于同日投稿至YouTube，再生数为 16,000+（最终记录）<br>" \
               "于2020年4月25日补档至YouTube，再生数为 16,000+"
        self.assertIsNone(find_youtube_count(text, log_error=False))
        text = "于同日投稿至Youtube，播放数为36,700+<br />于5月2日投稿于Bilibili，播放数为{{BilibiliCount|id=BV12g4y1q76w}}"
        s, e = find_youtube_count(text)
        self.assertEqual("36,700+", text[s:e])
        text = "<br />YouTube再生数为1,700,000+<br />"
        s, e = find_youtube_count(text)
        self.assertEqual("1,700,000+", text[s:e])
        text = "2013年12月26日在Youtube上發佈，再生數為276,600<br>" \
               "2013年12月27日投稿至niconico，再生數為{{NiconicoCount|id=sm22544683}}"
        s, e = find_youtube_count(text)
        self.assertEqual("276,600", text[s:e])
        text = "   1,000+  "
        s, e = find_youtube_count(text)
        self.assertEqual("1,000+", text[s:e])
