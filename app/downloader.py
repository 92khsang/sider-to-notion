from __future__ import annotations

from collections import defaultdict
from dataclasses import field, dataclass
from typing import TYPE_CHECKING, NamedTuple
from urllib.parse import urlparse, urljoin

import requests
from bs4 import BeautifulSoup

if TYPE_CHECKING:
    TAG_NAME: str
    ATTR_NAME: str
    ATTR_VALUE: str

    from bs4.element import Tag


class ExcludeTag(NamedTuple):
    tag: str
    attrs: dict[str, set[str]] = defaultdict(set)


@dataclass(frozen=True, slots=True)
class ExcludeTags:
    tags: list[ExcludeTag] = field(default_factory=list)

    @classmethod
    def from_list(
        cls, excludes: list[tuple[TAG_NAME, dict[ATTR_NAME, ATTR_VALUE]]]
    ) -> ExcludeTags:
        tags = []
        for exclude in excludes:
            tag, attrs = exclude
            attrs = {key: set(value.split(",")) for key, value in attrs.items()}
            tags.append(ExcludeTag(tag, attrs))
        return cls(tags)


def _request_html(url: str) -> BeautifulSoup:
    response = requests.get(url)

    try:
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise

    return BeautifulSoup(response.text, "html.parser")


def _exclude_tags(excludes: ExcludeTags, soup: BeautifulSoup) -> None:
    def decompose_tag(tags: list[Tag]) -> None:
        for tag_ in tags:
            tag_.decompose()

    for exclude in excludes.tags:
        if exclude.attrs:
            for key, value in exclude.attrs.items():
                decompose_tag(soup.find_all(exclude.tag, {key: value}))
        else:
            decompose_tag(soup.find_all(exclude.tag))


def _replace_links(base_url, soup: BeautifulSoup) -> None:
    for link_tag in ["link", "a", "img"]:
        for tag in soup.find_all(link_tag):
            href = tag.get("href")
            if href is None or ".." not in href:
                continue

            href = urljoin(base_url, href)

            tag["href"] = href


def download_html(
    excludes: ExcludeTags, url: str, html_str: str | None = None
) -> BeautifulSoup:
    """
    Download an HTML page and exclude the specified tags from the page.

    :param excludes: The tags are to be excluded from the page.
    :param url: The URL of the page to download.
    :param html_str: The HTML content of the page to parse. If None, the page is downloaded from the given URL.

    :return: The parsed HTML content of the page with the specified tags is excluded.
    """
    if html_str:
        html_soup = BeautifulSoup(html_str, "html.parser")
    else:
        parse_url = urlparse(url)
        if parse_url is None:
            raise ValueError(f"{url} is not a valid url")

        html_soup = _request_html(url)

    _exclude_tags(excludes, html_soup)
    _replace_links(url, html_soup)

    return html_soup
