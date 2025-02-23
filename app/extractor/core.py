from __future__ import annotations

from abc import abstractmethod
from collections import defaultdict
from copy import copy
from typing import override, TYPE_CHECKING

from bs4 import Tag

from app.core.decorators import singleton
from app.extractor.models import Element

if TYPE_CHECKING:
    from app.extractor.models import DivFilter


class ExtractError(Exception):
    pass


def _extract_translation(tag: Tag) -> str:
    return tag.find("sider-trans-text").text.strip()


def _decompose_translation(tag: Tag) -> None:
    element = tag.find("sider-trans")
    if element:
        element.decompose()


def _extract_attrs(tag: Tag) -> dict[str, list[str]]:
    attrs = tag.attrs
    extracted_attrs = defaultdict(list)
    for key, value in attrs.items():
        if isinstance(value, str):
            extracted_attrs[key].append(value)
        else:
            extracted_attrs[key].extend(value)

    return extracted_attrs


def _expand_tag(tag: Tag) -> Element:

    copied_tag = copy(tag)

    element = Element.from_element(copied_tag)

    while copied_tag.contents:
        child = copied_tag.contents[0]
        if isinstance(child, Tag):
            element.add_child(_expand_tag(child))
        else:
            element.add_child(Element.from_element(copy(child)))
        child.decompose()

    tag.decompose()
    return element


def _find_extractor(extractors: list[TagExtractor], tag: Tag) -> TagExtractor | None:
    for extractor in extractors:
        if extractor.is_extractable(tag):
            return extractor
    return None


def extract_to_element(
    extractors: list[TagExtractor], tag: Tag, parent: Element | None = None
) -> Element:
    """
    Recursively extract HTML tags to `Element` objects.

    :param extractors: a list of `TagExtractor` objects to use for extraction
    :param tag: the `Tag` object to extract
    :param parent: the `Element`
    object to append the extracted `Element` to, if any,

    :return: the extracted `Element` object
    """
    extractor = _find_extractor(extractors, tag)
    element = extractor.extract(tag) if extractor else None

    for original_child in tag.children:
        if not isinstance(original_child, Tag):
            continue

        child: Tag = copy(original_child)
        original_child.decompose()

        child_element: Element | None = extract_to_element(
            extractors, child, element or parent
        )
        if child_element:
            (
                element.add_child(child_element)
                if element
                else parent.add_child(child_element)
            )

    return element


# -- Extractor classes --
@singleton
class TagExtractor:

    def is_extractable(self, tag: Tag) -> bool:
        return True

    def extract(self, tag: Tag) -> Element:
        """
        Extract a `Tag` object into an `Element` object.

        :param tag: The `Tag` object to be extracted.
        :return: The extracted `Element` object.
        """
        return Element.from_element(tag)


class LastTagExtractor(TagExtractor):

    @override
    def extract(self, tag: Tag) -> Element:

        copied_tag = copy(tag)

        element = Element.from_element(copied_tag)
        while copied_tag.contents:
            child = copied_tag.contents[0]
            if isinstance(child, Tag):
                child_element = extract_to_element(self.extractors(), child, element)
                if child_element:
                    element.add_child(child_element)
                else:
                    element.add_child(_expand_tag(child))
            else:
                element.add_child(Element.from_element(child))
            child.decompose()

        tag.decompose()
        return element

    @abstractmethod
    def extractors(self) -> list[TagExtractor]: ...


class HTagExtractor(TagExtractor):
    @override
    def is_extractable(self, tag: Tag) -> bool:
        return tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]

    @override
    def extract(self, tag: Tag) -> Element:
        if not self.is_extractable(tag):
            raise ExtractError(f"{tag.name} is not supported")

        _decompose_translation(tag)
        return Element.from_element(tag)


class DivTagExtractor(TagExtractor):

    def __init__(self, filters: list[DivFilter]):
        super().__init__()
        self._filters = filters

    def _find_filter_value(self, tag: Tag) -> DivFilter | None:

        for id_filter in [f for f in self._filters if f.type == "id"]:
            if tag.attrs.get("id") == id_filter.value:
                return id_filter

        for class_filter in [f for f in self._filters if f.type == "class"]:
            for tag_classes in tag.attrs.get("class", []):
                if class_filter.value in tag_classes:
                    return class_filter

        return None

    @override
    def extract(self, tag: Tag) -> Element:
        div_filter = self._find_filter_value(tag)
        return Element.from_element(tag, div_filter.value)

    @override
    def is_extractable(self, tag: Tag) -> bool:
        if tag.name != "div":
            return False
        return self._find_filter_value(tag) is not None
