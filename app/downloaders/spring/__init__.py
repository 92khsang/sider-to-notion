from __future__ import annotations

from bs4 import BeautifulSoup
from typing_extensions import override

from app.downloaders.base import Downloader
from app.downloaders.models import ExcludeTags
from app.downloaders.utils import exclude_tags


class SpringDocDownloader(Downloader):
    EXCLUDE_TAGS: ExcludeTags = ExcludeTags.from_list(
        [
            ("div", {"class": "breadcrumbs-container"}),
            ("div", {"class": "nav-container"}),
            ("div", {"class": "toolbar"}),
            ("div", {"class": "modal"}),
            ("header", {"class": "header"}),
            ("footer", {"class": "footer"}),
            ("aside", {"class": "sidebar"}),
            ("aside", {"class": "toc embedded"}),
            ("span", {"class": "copy-toast"}),
            ("script", {}),
            ("a", {"class": "anchor"}),
            ("chatgpt-sidebar", {}),
            ("chatgpt-sidebar-popups", {}),
            ("button", {"class": "copy-button"}),
        ]
    )

    @override
    def exclude_tags(self, soup: BeautifulSoup) -> None:
        exclude_tags(self.EXCLUDE_TAGS, soup)


__all__ = ["SpringDocDownloader"]
