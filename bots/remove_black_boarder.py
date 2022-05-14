import json
import urllib.parse
from pathlib import Path

import numpy as np
import requests
import wikitextparser as wtp

from bots.common import run_vj_bot
from utils.image import download_file
from utils.logger import get_logger
from utils.wikitext import get_template_by_name
from web.mgp import get_page


def get_bounding_rect(gray, crop_threshold: float) -> (int, int, int, int):
    # use np to sum rows until row sum exceeds a threshold
    # no column support for now
    def get_row_num(start: int, step: int) -> int:
        index = start
        while 0 <= index < len(gray):
            s = np.sum(gray[index])
            average = s / len(gray[index])
            if average > crop_threshold:
                return index
            index += step

    y1, y2 = get_row_num(0, 1), get_row_num(len(gray) - 1, -1)
    x1, x2 = 0, len(gray[0])
    return x1, x2, y1, y2


def remove_black_boarders(image_in: str, image_out: str, crop_threshold: float) -> bool:
    # img = cv2.imread(image_in)
    # TODO: show image in a loop and let user decide
    # gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # x1, x2, y1, y2 = get_bounding_rect(gray, crop_threshold)
    # crop = img[y1:y2, x1:x2]

    # cv2.imwrite(image_out, crop)
    raise NotImplementedError("Wait till this feature is implemented.")
    return True


def get_image_names(text: str) -> list[str]:
    parsed = wtp.parse(text)
    song_boxes = get_template_by_name(parsed, "VOCALOID_Songbox")
    result = []
    for song_box in song_boxes:
        arg = song_box.get_arg("image")
        if arg is None:
            continue
        result.append(arg.value)
    return result


def convert_image(source: str):
    base_url = "commons.moegirl.org.cn/api.php?action=query&format=json&list=allimages&aifrom={}&ailimit=1"
    url = base_url.format(urllib.parse.quote(source))
    response = json.loads(requests.get(url).text)
    image = response['query']['allimages'][0]
    image_name = image['name']
    if image_name != source:
        get_logger().error("Queried file name {} does not match expected file name {}.".format(image_name, source))
        return
    image_url = image['url']
    temp_path = Path("cache/temp_" + image_name)
    image_out = Path("cache/" + image_name)
    download_file(image_url, temp_path)
    res = remove_black_boarders(str(temp_path), str(image_out), 25)
    if res:
        pass


def process_song(name: str):
    page = get_page(name)
    image_names = get_image_names(page.wikitext)
    for name in image_names:
        convert_image(name)


def remove_black_boarder_bot():
    run_vj_bot(process_song)
