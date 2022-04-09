import pywikibot

import config.config
from bots.auto_furigana import auto_furigana
from bots.youtube_fallback import youtube_fallback
from config.config import Mode
from utils import login
from utils.caching import init_caching
from utils.logger import setup_logger

site = pywikibot.Site()


def main():
    setup_logger()
    init_caching()
    login.main()
    m = {
        Mode.AUTO_FURIGANA: auto_furigana,
        Mode.AUTO_YOUTUBE_FALLBACK: youtube_fallback
    }
    m[config.config.mode]()


if __name__ == "__main__":
    main()
