from __future__ import annotations

from copy import copy
from typing import override, TYPE_CHECKING

from bs4 import Tag

from app.extractor import (
    LastTagExtractor,
    TagExtractor,
    HTagExtractor,
    DivTagExtractor,
)
from app.extractor.models import DivFilter

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SpringDivTagExtractor(DivTagExtractor):
    DIV_FILTERS: list[DivFilter] = [
        DivFilter(value="preamble", type="id"),
        DivFilter("sect1"),
        DivFilter("paragraph"),
        DivFilter("sect2"),
        DivFilter("tabs"),
        DivFilter("title"),
    ]

    def __init__(self):
        super().__init__(self.DIV_FILTERS)


class SpringBaseTagExtractor(TagExtractor):
    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name in ["article"]


class SpringLastTagExtractor(LastTagExtractor):

    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name in [
            "p",
            "a",
            "span",
            "code",
            "sider-trans-text",
            "table",
            "img",
        ]

    @override
    def extractors(self) -> list[TagExtractor]:
        return tag_extractors()


_SPRING_TAG_EXTRACTORS = [
    HTagExtractor(),
    SpringBaseTagExtractor(),
    SpringDivTagExtractor(),
    SpringLastTagExtractor(),
]


def tag_extractors() -> list[TagExtractor]:
    return _SPRING_TAG_EXTRACTORS


def root_tag(soup: BeautifulSoup) -> Tag:
    return copy(soup.find("article", attrs={"class": "doc"}))


__all__ = ["tag_extractors", "root_tag"]
