from __future__ import annotations

from typing import override, TYPE_CHECKING

from bs4 import BeautifulSoup

from app import extractor, downloader
from app.docs import DocProcessor, add_processor, DocType
from app.docs.spring import spring_extractor
from app.downloader import ExcludeTags
from app.extractor.models import Element

if TYPE_CHECKING:
    from app.notion.models import NotionProperty

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


class SpringDocProcessor(DocProcessor):

    @override
    def read(self, url: str, html_str: str | None = None) -> BeautifulSoup:
        return downloader.download_html(EXCLUDE_TAGS, url, html_str)

    @override
    def extract(self, html_soup: BeautifulSoup) -> Element:
        return extractor.extract_to_element(
            spring_extractor.tag_extractors(), spring_extractor.root_tag(html_soup)
        )

    @override
    def write(self, element: Element, properties: set[NotionProperty]) -> None:
        pass


add_processor(DocType.SPRING, SpringDocProcessor())

__all__ = []
