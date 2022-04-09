from unittest import TestCase

import wikitextparser
from wikitextparser import Template

from bots.youtube_fallback import update_yt_count, add_youtube_count, convert_views
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
|其他资料 = 于同日投稿至YouTube，再生数为{{{{YoutubeCount|id=Gexhf83mq3M|fallback={get_yt_views(yt_id)}}}}}+<br/>于}}}}"""
        t = Template(wikitext)
        add_youtube_count(t)
        self.assertEqual(expected, t.string)

