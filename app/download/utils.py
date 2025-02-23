from __future__ import annotations

from typing import TYPE_CHECKING

import requests
from bs4 import BeautifulSoup

from app.download.models import ExcludeTags

if TYPE_CHECKING:
    from bs4 import Tag


def request_html(url: str) -> BeautifulSoup:
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise

    return BeautifulSoup(response.text, "html.parser")


def exclude_tags(excludes: ExcludeTags, soup: BeautifulSoup) -> None:
    def decompose_tag(tags: list[Tag]) -> None:
        for tag_ in tags:
            tag_.decompose()

    for exclude in excludes.tags:
        if exclude.attrs:
            for key, value in exclude.attrs.items():
                decompose_tag(soup.find_all(exclude.tag, {key: value}))
        else:
            decompose_tag(soup.find_all(exclude.tag))
