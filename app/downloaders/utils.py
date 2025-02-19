from __future__ import annotations

import requests
from bs4 import BeautifulSoup

from app.downloaders.models import ExcludeTags


def request_html(url: str) -> BeautifulSoup:
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise

    return BeautifulSoup(response.text, "html.parser")


def exclude_tags(excludes: ExcludeTags, soup: BeautifulSoup) -> None:
    for exclude in excludes.tags:
        for key, value in exclude.attrs.items():
            for tag in soup.find_all(exclude.tag, {key: value}):
                tag.decompose()
