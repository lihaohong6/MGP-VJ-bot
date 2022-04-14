from pathlib import Path

import requests


def download_file(url: str, target: str | Path) -> bool:
    with requests.get(url, stream=True) as r:
        r.raise_for_status()
        with open(target, 'wb') as f:
            for chunk in r.iter_content(chunk_size=8192):
                f.write(chunk)
    return True
