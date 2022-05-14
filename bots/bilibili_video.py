import urllib.parse
import webbrowser

import bs4
import requests
from pywikibot import Page

from bots.common import run_vj_bot
from utils.wikitext import get_template_by_name
from web.mgp import get_pages_embedded, MGPPage
import wikitextparser as wtp


def process_page(page_name: str):
    page = MGPPage(page_name)
    parsed = wtp.parse(page.wikitext)
    templates = get_template_by_name(parsed, "BilibiliVideo")
    for t in templates:
        bid = t.get_arg("id").value
        response = requests.get("https://www.bilibili.com/video/" + bid).text
        parsed = bs4.BeautifulSoup(response, "html.parser")
        errors = parsed.find_all("div", {"class": "error-body"})
        if len(errors) > 0:
            webbrowser.open("https://zh.moegirl.org.cn/" + urllib.parse.quote(page.title))


def bilibili_video():
    run_vj_bot(process_page, fetch_song_list=lambda: get_pages_embedded("T:BilibiliVideo"))


if __name__ == "__main__":
    bilibili_video()
