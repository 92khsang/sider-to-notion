from __future__ import annotations as _annotations

from abc import ABC
from collections import deque
from typing import Optional, Self, Union
from weakref import proxy

from bs4.element import PageElement, Tag, NavigableString
from pydantic import BaseModel, Field, ConfigDict, computed_field

__all__ = ["TagElement", "NavStringElement", "Element"]


class Element(BaseModel, ABC):
    model_config = ConfigDict(arbitrary_types_allowed=True, extra="forbid")

    classification: str
    element: PageElement = Field(exclude=True)
    parent: Optional[Union[TagElement, NavStringElement]] = Field(
        default=None, exclude=True
    )
    children: deque[Union[TagElement, NavStringElement]] = Field(default_factory=deque)

    def add_child(self, child: Union[TagElement, NavStringElement]) -> None:
        child.parent = proxy(self)
        self.children.append(child)

    def text(self, strip: bool = False) -> str:
        return self.element.get_text(strip=strip)


class TagElement(Element):
    element: Tag = Field(exclude=True)

    def __init__(self, tag: Tag, classification: Optional[str] = None):
        super().__init__(element=tag, classification=classification or tag.name)

    @computed_field
    @property
    def tag_name(self) -> str:
        return self.element.name

    @computed_field
    @property
    def attrs(self) -> dict[str, list[str]]:
        return self.element.attrs

    @property
    def id(self) -> Optional[str]:
        value = self.attrs.get("id")
        return value[0] if isinstance(value, list) and value else None

    @property
    def classes(self) -> list[str]:
        return self.attrs.get("class", [])

    @property
    def tag_children(self) -> list[Self]:
        return [c for c in self.children if isinstance(c, TagElement)]


class NavStringElement(Element):
    element: NavigableString = Field(exclude=True)

    def __init__(self, nav_string: NavigableString):
        super().__init__(element=nav_string, classification="nav_string")

    @computed_field
    @property
    def nav_string(self) -> str:
        return self.element.get_text()
