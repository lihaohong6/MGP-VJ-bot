from bots.common import run_vj_bot, run_with_waf, throttle
from utils.input_utils import prompt_response
from utils.string_utils import is_empty
from web.mgp import get_pages_embedded, get_page, save_edit, get_references
import wikitextparser as wtp


def process_page(page_name: str):
    page = get_page(page_name)
    # parsed = wtp.parse(page.wikitext)
    # for link in parsed.wikilinks:
    #     if link.title == 'Alicesoft':
    #         link.title = 'AliceSoft'
    parsed = (page.wikitext
              .replace("Alicesoft", "AliceSoft")
              .replace("ALICE-SOFT", "AliceSoft"))
    throttle(21)
    save_edit(str(parsed), page, "统一[[AliceSoft]]拼写",
              confirm=False, minor=True, tags="Bot")


def replace_links():
    run_vj_bot(process_page, fetch_song_list=lambda: get_references("ALICE-SOFT"))
