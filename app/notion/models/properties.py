from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeAlias

from app.notion.models import RichText
from app.notion.types import PropertyType, Color

PropertyId: TypeAlias = str


@dataclass
class SelectItem:
    name: str
    id: str | None = field(default=None)
    color: Color | None = field(default=None)


@dataclass
class NotionProperty:
    name: str
    pid: PropertyId | None
    ptype: PropertyType

    @property
    def id(self):
        return self.pid

    @property
    def type(self):
        return self.ptype

    def __hash__(self):
        return hash(self.name)


@dataclass
class TitleProperty(NotionProperty):
    rich_text: RichText
    ptype: PropertyType = field(default=PropertyType.TITLE)


@dataclass
class SelectProperty(NotionProperty):
    item: SelectItem
    ptype: PropertyType = field(default=PropertyType.SELECT)


@dataclass
class UrlProperty(NotionProperty):
    url: str
    ptype: PropertyType = field(default=PropertyType.URL)


@dataclass
class MultipleSelectProperty(NotionProperty):
    items: list[SelectItem]
    ptype: PropertyType = field(default=PropertyType.MULTIPLE_SELECT)
