from __future__ import annotations

from typing import override, NamedTuple

from bs4 import Tag

from app.converters.base import (
    LastTagConverter,
    TagConverter,
    HTagConverter,
)


class SpringDivFilter(NamedTuple):
    value: str
    type: str = "class"


class SpringDivTagConverter(TagConverter):
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
    def is_convertable(self, tag: Tag) -> bool:
        if tag.name != "div":
            return False
        return self._find_filter_value(tag) is not None


class SpringBaseTagConverter(TagConverter):
    @override
    def is_convertable(self, tag: Tag) -> bool:
        return tag.name in ["article"]


class SpringLastTagConverter(LastTagConverter):

    @override
    def is_convertable(self, tag: Tag) -> bool:
        return tag.name in ["p", "a", "code", "sider-trans-text"]

    @override
    def converters(self) -> list[TagConverter]:
        return SPRING_TAG_CONVERTERS


SPRING_TAG_CONVERTERS = [
    HTagConverter(),
    SpringBaseTagConverter(),
    SpringDivTagConverter(),
    SpringLastTagConverter(),
]
