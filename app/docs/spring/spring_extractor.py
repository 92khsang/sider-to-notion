from __future__ import annotations

from copy import copy
from typing import override, NamedTuple, TYPE_CHECKING

from bs4 import Tag

from app.extractor import (
    LastTagExtractor,
    TagExtractor,
    HTagExtractor,
)

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class SpringDivFilter(NamedTuple):
    value: str
    type: str = "class"


class SpringDivTagExtractor(TagExtractor):
    DIV_FILTERS: list[SpringDivFilter] = [
        SpringDivFilter(value="preamble", type="id"),
        SpringDivFilter("sect1"),
        SpringDivFilter("paragraph"),
        SpringDivFilter("note"),
        SpringDivFilter("sect2"),
        SpringDivFilter("content"),
        SpringDivFilter("tabs"),
        SpringDivFilter("title"),
    ]

    def _find_filter_value(self, tag) -> SpringDivFilter | None:
        for id_filter in [f for f in self.DIV_FILTERS if f.type == "id"]:
            if tag.attrs.get("id") == id_filter.value:
                return id_filter

        for class_filter in [f for f in self.DIV_FILTERS if f.type == "class"]:
            for tag_classes in tag.attrs.get("class", []):
                if class_filter.value in tag_classes:
                    return class_filter

        return None

    @override
    def is_extractable(self, tag: Tag) -> bool:
        if tag.name != "div":
            return False
        return self._find_filter_value(tag) is not None


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
