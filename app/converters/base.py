from __future__ import annotations

from abc import ABCMeta, abstractmethod
from copy import copy
from typing import TYPE_CHECKING, override

from bs4 import Tag

from app.converters.models import Element
from app.converters.utils import decompose_translation

if TYPE_CHECKING:
    from bs4 import BeautifulSoup


class ConvertError(Exception):
    pass


class DocConverter(metaclass=ABCMeta):
    def __init__(self, soup: BeautifulSoup):
        self.soup = soup

    def convert(self) -> Element:
        """Convert the root tag into an Element object.

        The conversion is done by calling: func:`convert_tags_to_element` with the
        converters and the root tag. The method is abstract and must be
        implemented by subclasses.

        :return: The Element object representing the root tag.
        """
        return convert_to_element(self.converters, self.root_tag)

    @property
    @abstractmethod
    def root_tag(self) -> Tag: ...

    @property
    @abstractmethod
    def converters(self) -> list[TagConverter]: ...


def find_converter(converters: list[TagConverter], tag: Tag) -> TagConverter | None:
    for converter in converters:
        if converter.is_convertable(tag):
            return converter
    return None


def convert_to_element(
    converters: list[TagConverter], tag: Tag, parent: Element | None = None
) -> Element:
    """
    Recursively convert HTML tags to `Element` objects.

    :param converters: a list of `TagConverter` objects to use for conversion
    :param tag: the `Tag` object to convert
    :param parent: the `Element`
    object to append the converted `Element` to, if any,

    :return: the converted `Element` object
    """
    converter = find_converter(converters, tag)
    element = converter.convert(tag) if converter else None

    for original_child in tag.children:
        if not isinstance(original_child, Tag):
            continue

        child: Tag = copy(original_child)
        original_child.decompose()

        child_element: Element | None = convert_to_element(
            converters, child, element or parent
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


class TagConverter:

    def is_convertable(self, tag: Tag) -> bool:
        return True

    def convert(self, tag: Tag) -> Element:
        """
        Convert a `Tag` object into an `Element` object.

        :param tag: The `Tag` object to be converted.
        :return: The converted `Element` object.
        """
        return Element.from_element(tag)


class LastTagConverter(TagConverter):

    @override
    def convert(self, tag: Tag) -> Element:

        copied_tag = copy(tag)

        element = Element.from_element(copied_tag)
        while copied_tag.contents:
            child = copied_tag.contents[0]
            if isinstance(child, Tag):
                child_element = convert_to_element(self.converters(), child, element)
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
    def converters(self) -> list[TagConverter]: ...


class HTagConverter(TagConverter):
    @override
    def is_convertable(self, tag: Tag) -> bool:
        return tag.name in ["h1", "h2", "h3", "h4", "h5", "h6"]

    @override
    def convert(self, tag: Tag) -> Element:
        if not self.is_convertable(tag):
            raise ConvertError(f"{tag.name} is not supported")

        decompose_translation(tag)
        return Element.from_element(tag)
