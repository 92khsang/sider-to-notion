from __future__ import annotations

from typing import override, NamedTuple

from bs4 import Tag

from app.extract.base import (
    LastTagExtractor,
    TagExtractor,
    HTagExtractor,
)


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
        return SPRING_TAG_EXTRACTORS


SPRING_TAG_EXTRACTORS = [
    HTagExtractor(),
    SpringBaseTagExtractor(),
    SpringDivTagExtractor(),
    SpringLastTagExtractor(),
]
