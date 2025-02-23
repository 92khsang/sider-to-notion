from __future__ import annotations

import weakref
from abc import (
    ABC,
)
from collections import deque
from typing import TYPE_CHECKING

from bs4.element import (
    NavigableString,
    Tag,
)

if TYPE_CHECKING:
    from bs4.element import PageElement


class Element(ABC):
    def __new__(cls, *args, **kwargs):
        if cls is Element:
            raise TypeError(
                "Element is an abstract class and cannot be instantiated directly."
            )
        return super().__new__(cls)

    def __init__(self, element: PageElement):
        self._element = element
        self._parent: weakref.ProxyType[Element] | None = None
        self._children: deque[Element] = deque()

    def add_child(self, child: Element) -> None:
        """
        Add a child `Element` to this `Element`.

        This method appends the given child `Element` to the list of children
        and sets the parent of the child to this `Element`.

        :param child: The `Element` to be added as a child.
        """
        child._parent = weakref.proxy(self)
        self._children.append(child)

    def text(self, strip: bool = False) -> str:
        return self._element.get_text(strip=strip)

    @property
    def parent(self) -> Element | None:
        return self._parent

    @property
    def children(self) -> deque[Element]:
        return self._children

    @property
    def element(self) -> PageElement:
        return self._element

    @classmethod
    def from_element(cls, element: PageElement) -> Element:
        if isinstance(element, Tag):
            return TagElement(element)
        elif isinstance(element, NavigableString):
            return NavStringElement(element)

        raise ValueError(f"Unsupported element type: {type(element)}")


class TagElement(Element):
    if TYPE_CHECKING:
        _element: Tag

    def __init__(self, tag: Tag):
        super().__init__(tag)

    @property
    def tag_name(self) -> str:
        return self._element.name

    @property
    def attrs(self) -> dict[str, list[str]]:
        return self._element.attrs

    @property
    def id(self) -> str | None:
        return self.attrs.get("id", [None])[0]

    @property
    def classes(self) -> list[str]:
        return self.attrs.get("class", [])


class NavStringElement(Element):
    if TYPE_CHECKING:
        _element: NavigableString

    def __init__(self, nav_string: NavigableString):
        super().__init__(nav_string)
