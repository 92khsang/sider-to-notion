from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup
from bs4.element import Tag

from .model import ExcludeTags


def _request_html(url: str) -> BeautifulSoup:
    response = requests.get(url)
    response.raise_for_status()
    return BeautifulSoup(response.text, "html.parser")


def _exclude_tags(excludes: ExcludeTags, soup: BeautifulSoup) -> None:
    def decompose_tag(tags: list[Tag]) -> None:
        for tag_ in tags:
            tag_.decompose()

    for exclude in excludes.tags:
        if exclude.attrs:
            for key, values in exclude.attrs.items():
                for value in values:
                    decompose_tag(soup.find_all(exclude.tag, {key: value}))
        else:
            decompose_tag(soup.find_all(exclude.tag))


def _replace_links(base_url: str, soup: BeautifulSoup) -> None:
    for link_tag in ["link", "a", "img"]:
        attr = "href" if link_tag in ["link", "a"] else "src"
        for tag in soup.find_all(link_tag):
            url = tag.get(attr)
            if url and not url.startswith("http"):
                tag[attr] = urljoin(base_url, url)


def fetch_html(
    excludes: ExcludeTags, url: str, html_str: str | None = None
) -> BeautifulSoup:
    """Fetch an HTML page and exclude the specified tags from the page.

    Args:
        excludes (ExcludeTags): The tags are to be excluded from the page.
        url (str): The URL of the page to fetch.
        html_str (str, optional): The HTML content of the page to parse. If None, the page is fetched from the given URL.

    Returns:
        BeautifulSoup: The parsed HTML content of the page with the specified tags is excluded.
    """
    soup = BeautifulSoup(html_str, "html.parser") if html_str else _request_html(url)

    _exclude_tags(excludes, soup)
    _replace_links(url, soup)
    return soup
