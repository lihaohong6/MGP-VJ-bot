from typing import Union

import requests
from bs4 import BeautifulSoup

from utils.logger import get_logger


def get_yt_views(vid: str) -> Union[int, None]:
    vid = vid.strip()
    if vid.find("youtube.") != -1:
        vid = vid[vid.find("=") + 1:]
    elif vid.find("youtu.be") != -1:
        vid = vid[vid.rfind("/") + 1:]
    url = 'https://www.youtube.com/watch?v=' + vid
    text = requests.get(url).text
    soup = BeautifulSoup(text, "html.parser")
    interaction = soup.select_one('meta[itemprop="interactionCount"][content]')
    views = int(interaction['content'])
    return views
