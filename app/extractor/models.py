from __future__ import annotations

import weakref
from abc import ABCMeta
from collections import deque
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, NamedTuple, Literal

from bs4.element import (
    NavigableString,
    Tag,
)

if TYPE_CHECKING:
    from bs4.element import PageElement


class DivFilter(NamedTuple):
    value: str
    type: Literal["id", "class"] = "class"


@dataclass
class Element(metaclass=ABCMeta):
    element: PageElement
    classification: str
    parent: weakref.ProxyType[Element] | None = field(init=False, default=None)
    children: deque[Element] = field(init=False, default_factory=deque)

    def __new__(cls, *args, **kwargs):
        if cls is Element:
            raise TypeError(
                "Element is an abstract class and cannot be instantiated directly."
            )
        return super().__new__(cls)

    def add_child(self, child: Element) -> None:
        """
        Add a child `Element` to this `Element`.

        This method appends the given child `Element` to the list of children
        and sets the parent of the child to this `Element`.

        :param child: The `Element` to be added as a child.
        """
        child.parent = weakref.proxy(self)
        self.children.append(child)

    def text(self, strip: bool = False) -> str:
        return self.element.get_text(strip=strip)

    @classmethod
    def from_element(
        cls, element: PageElement, classification: str | None = None
    ) -> Element:
        if isinstance(element, Tag):
            return TagElement(element, classification)
        elif isinstance(element, NavigableString):
            return NavStringElement(element)

        raise ValueError(f"Unsupported element type: {type(element)}")


class TagElement(Element):
    if TYPE_CHECKING:
        element: Tag

    def __init__(self, tag: Tag, classification: str | None = None):
        super().__init__(tag, classification or tag.name)

    @property
    def tag_name(self) -> str:
        return self.element.name

    @property
    def attrs(self) -> dict[str, list[str]]:
        return self.element.attrs

    @property
    def id(self) -> str | None:
        return self.attrs.get("id", [None])[0]

    @property
    def classes(self) -> list[str]:
        return self.attrs.get("class", [])


class NavStringElement(Element):
    if TYPE_CHECKING:
        element: NavigableString

    def __init__(self, nav_string: NavigableString):
        super().__init__(nav_string, "nav_string")
