from __future__ import annotations

from abc import ABCMeta, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, override

from bs4 import Tag

from app.extract.models import Element
from app.extract.utils import decompose_translation

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class ExtractError(Exception):
    pass


class DocExtractor(metaclass=ABCMeta):
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def extract(self) -> Element:
        """Extract the root tag into an Element object.

        The extraction is done by calling: func:`extract_tags_to_element` with the
        extractors and the root tag.
        The method is abstract and must be implemented by subclasses.

        :return: The Element object representing the root tag.
        """
        return extract_to_element(self.extractors, self.root_tag)

    @property
    @abstractmethod
    def root_tag(self) -> Tag: ...

    @property
    @abstractmethod
    def extractors(self) -> list[TagExtractor]: ...


def find_extractor(extractors: list[TagExtractor], tag: Tag) -> TagExtractor | None:
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
    extractor = find_extractor(extractors, tag)
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


def expand_tag(tag: Tag) -> Element:

    copied_tag = copy(tag)

    element = Element.from_element(copied_tag)

    while copied_tag.contents:
        child = copied_tag.contents[0]
        if isinstance(child, Tag):
            element.add_child(expand_tag(child))
        else:
            element.add_child(Element.from_element(copy(child)))
        child.decompose()

    tag.decompose()
    return element


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
                    element.add_child(expand_tag(child))
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

        decompose_translation(tag)
        return Element.from_element(tag)
