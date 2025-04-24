from copy import copy
from typing import override

from bs4 import Tag, BeautifulSoup

from sider_to_notion.extractor import DivFilter
from sider_to_notion.extractor import (
    LastTagExtractor,
    TagExtractor,
    HTagExtractor,
    DivTagExtractor,
    TagElement,
)


class SpringDivTagExtractor(DivTagExtractor):
    DIV_FILTERS: list[DivFilter] = [
        DivFilter(value="preamble", type="id"),
        DivFilter(value="sect1"),
        DivFilter(value="sect2"),
        DivFilter(value="sect3"),
        DivFilter(value="sect4"),
        DivFilter(value="section-summary", classification="sect1"),
        DivFilter(value="paragraph"),
        DivFilter(value="listingblock"),
        DivFilter(value="imageblock"),
        DivFilter(value="exampleblock"),
        DivFilter(value="tabs"),
        DivFilter(value="content"),
        DivFilter(value="tablist"),
        DivFilter(value="ulist"),
        DivFilter(value="colist"),
        DivFilter(value="olist"),
        DivFilter(value="admonitionblock"),
    ]

    def __init__(self):
        super().__init__(self.DIV_FILTERS)


class SpringBaseTagExtractor(TagExtractor):
    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name in ["article"]


class SpringTitleTagExtractor(LastTagExtractor):
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name == "div" and "title" in tag.attrs.get("class", [])

    @override
    def extractors(self) -> list[TagExtractor]:
        return tag_extractors()

    @override
    def extract(self, tag: Tag) -> TagElement:
        element = super().extract(tag)
        element.classification = "title"
        return element


class SpringLastTagExtractor(LastTagExtractor):
    EXTRACT_TAG_MAP = {
        "p": "p",
        "a": "a",
        "span": "span",
        "sider-trans-text": "p",
        "table": "table",
        "thead": "thead",
        "tbody": "tbody",
        "th": "th",
        "tr": "tr",
        "td": "td",
        "img": "img",
        "ul": "ul",
        "ol": "ol",
        "li": "li",
    }

    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name in self.EXTRACT_TAG_MAP

    @override
    def extractors(self) -> list[TagExtractor]:
        return tag_extractors()

    @override
    def extract(self, tag: Tag) -> TagElement:
        classification = self.EXTRACT_TAG_MAP[tag.name]

        element = super().extract(tag)
        element.classification = classification
        return element


class SpringCodeTagExtractor(LastTagExtractor):
    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name == "code"

    @override
    def extractors(self) -> list[TagExtractor]:
        return tag_extractors()

    @override
    def extract(self, tag: Tag) -> TagElement:
        element = super().extract(tag)
        if element.attrs.get("data-lang", None):
            element.classification = "code_block"
        return element


def tag_extractors() -> list[TagExtractor]:
    return [
        HTagExtractor(),
        SpringBaseTagExtractor(),
        SpringDivTagExtractor(),
        SpringTitleTagExtractor(),
        SpringLastTagExtractor(),
        SpringCodeTagExtractor(),
    ]


def root_tag(soup: BeautifulSoup) -> Tag:
    return copy(soup.find("article", attrs={"class": "doc"}))


__all__ = ["tag_extractors", "root_tag"]
