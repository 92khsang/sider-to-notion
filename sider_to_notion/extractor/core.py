from abc import ABC, abstractmethod
from copy import copy
from typing import override, Optional

from bs4.element import Tag, NavigableString

from .filters import DivFilter
from .model import TagElement, NavStringElement

__all__ = [
    "extract_to_element",
    "find_div_filter",
    "ExtractError",
    "TagExtractor",
    "LastTagExtractor",
    "HTagExtractor",
    "DivTagExtractor",
]


class ExtractError(Exception):
    pass


def _extract_translation(tag: Tag) -> str:
    return tag.find("sider-trans-text").text.strip()


def _decompose_translation(tag: Tag) -> None:
    trans_tag = tag.find("sider-trans")
    if trans_tag:
        trans_tag.decompose()


def _expand_tag(tag: Tag) -> TagElement:
    copied = copy(tag)
    element = TagElement(copied)

    while copied.contents:
        child = copied.contents[0]
        if isinstance(child, Tag):
            element.add_child(_expand_tag(child))
        elif isinstance(child, NavigableString):
            element.add_child(NavStringElement(copy(child)))
        child.decompose()

    tag.decompose()
    return element


def _find_extractor(
    extractors: list["TagExtractor"], tag: Tag
) -> Optional["TagExtractor"]:
    for ext in extractors:
        if ext.is_extractable(tag):
            return ext
    return None


def extract_to_element(
    extractors: list["TagExtractor"], tag: Tag, parent: TagElement | None = None
) -> TagElement:
    extractor = _find_extractor(extractors, tag)
    element = extractor.extract(tag) if extractor else None

    for original_child in tag.children:
        if not isinstance(original_child, Tag):
            continue

        child_tag = copy(original_child)
        original_child.decompose()

        child_element = extract_to_element(extractors, child_tag, element or parent)
        if child_element:
            (element or parent).add_child(child_element)

    return element


def find_div_filter(tag: Tag, filters: list[DivFilter]) -> Optional[DivFilter]:
    for id_filter in [f for f in filters if f.type == "id"]:
        if tag.attrs.get("id") == id_filter.value:
            return id_filter

    for class_filter in [f for f in filters if f.type == "class"]:
        for tag_classes in tag.attrs.get("class", []):
            if class_filter.value in tag_classes:
                return class_filter

    return None


class TagExtractor(ABC):
    def is_extractable(self, tag: Tag) -> bool:
        return True

    def extract(self, tag: Tag) -> TagElement:
        return TagElement(tag)


class LastTagExtractor(TagExtractor):
    """
    Composite extractor that delegates to a list of child extractors.
    Falls back to `_expand_tag()` if no extractor matches.
    """

    @override
    def extract(self, tag: Tag) -> TagElement:
        copied_tag = copy(tag)
        element = TagElement(copied_tag)

        while copied_tag.contents:
            child = copied_tag.contents[0]

            if isinstance(child, Tag):
                child_element = extract_to_element(self.extractors(), child, element)

                if child_element:
                    element.add_child(child_element)
                else:
                    element.add_child(_expand_tag(child))

            elif isinstance(child, NavigableString):
                element.add_child(NavStringElement(copy(child)))

            child.decompose()

        tag.decompose()
        return element

    @abstractmethod
    def extractors(self) -> list[TagExtractor]:
        """
        Subclasses must define which extractors are used internally.
        """
        ...


class HTagExtractor(TagExtractor):
    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name in {"h1", "h2", "h3", "h4", "h5", "h6"}

    @override
    def extract(self, tag: Tag) -> TagElement:
        if not self.is_extractable(tag):
            raise ExtractError(f"{tag.name} is not supported")

        _decompose_translation(tag)

        tag = _expand_tag(tag)
        tag.classification = "heading"

        return tag


class DivTagExtractor(TagExtractor):
    def __init__(self, filters: list[DivFilter]):
        self._filters = filters

    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name == "div" and find_div_filter(tag, self._filters) is not None

    @override
    def extract(self, tag: Tag) -> TagElement:
        div_filter: Optional[DivFilter] = find_div_filter(tag, self._filters)
        if div_filter:
            classification: str = (
                div_filter.classification
                if div_filter.classification
                else div_filter.value
            )
        else:
            classification = "div"

        return TagElement(tag, classification)
