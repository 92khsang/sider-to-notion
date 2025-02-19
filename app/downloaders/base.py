from __future__ import annotations

from abc import ABCMeta, abstractmethod
from pathlib import Path
from urllib.parse import urlparse, urljoin

from bs4 import BeautifulSoup

from app.downloaders.utils import request_html


class Downloader(metaclass=ABCMeta):
    def download_html(
        self, url: str, downloaded_html: Path | None = None
    ) -> BeautifulSoup:

        if (
            downloaded_html
            and downloaded_html.is_file()
            and downloaded_html.suffix == ".html"
        ):
            html_soup = BeautifulSoup(downloaded_html.read_text(), "html.parser")
        else:
            parse_url = urlparse(url)
            if parse_url is None:
                raise ValueError(f"{url} is not a valid url")

            html_soup = request_html(url)

        self.exclude_tags(html_soup)
        self.replace_links(url, html_soup)

        return html_soup

    @abstractmethod
    def exclude_tags(self, soup: BeautifulSoup) -> None:
        raise NotImplementedError("exclude_tags are not implemented")

    @staticmethod
    def replace_links(base_url, soup: BeautifulSoup) -> None:
        for link_tag in ["link", "a"]:
            for tag in soup.find_all(link_tag):
                href = tag.get("href")
                if href is None or ".." not in href:
                    continue

                href = urljoin(base_url, href)

                tag["href"] = href
