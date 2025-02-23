from __future__ import annotations

import uuid
from dataclasses import dataclass
from typing import Literal

from app.notion.models import RichText, NotionParent, NotionId, NotionEmoji, NotionFile
from app.notion.types import RichColor, BlockType, LanguageType


@dataclass
class NotionBlock:
    type: BlockType
    id: NotionId | None
    parent: NotionParent | None

    def to_dict(self) -> dict:
        return {
            "object": "block",
            "type": self.type.value,
            **({"id": str(self.id)} if self.id else {}),
            **({"parent": self.parent.to_dict()} if self.parent else {}),
        }


@dataclass
class RichTextsBlock:
    rich_texts: list[RichText]

    def __init__(self, rich_texts: list[RichText] | None = None):
        self.rich_texts = rich_texts or []

    def add_rich_text(self, rich_text: RichText) -> None:
        self.rich_texts.append(rich_text)

    def to_dict(self) -> dict:
        return {"rich_text": [r.to_dict() for r in self.rich_texts]}


@dataclass
class HierarchicalBlock:
    children: list[NotionBlock]

    def __init__(self, children: list[NotionBlock] | None = None):
        self.children = children or []

    def add_child(self, child: NotionBlock) -> None:
        self.children.append(child)

    def to_dict(self) -> dict:
        return {"children": [c.to_dict() for c in self.children]}


@dataclass
class Paragraph(NotionBlock, RichTextsBlock, HierarchicalBlock):
    color: RichColor

    def __init__(
        self,
        rich_texts: list[RichText] | None = None,
        color: RichColor = RichColor.DEFAULT,
        children: list[NotionBlock] | None = None,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.PARAGRAPH, block_id, parent)
        RichTextsBlock.__init__(self, rich_texts)
        HierarchicalBlock.__init__(self, children)
        self.color = color

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                **RichTextsBlock.to_dict(self),
                **HierarchicalBlock.to_dict(self),
                "color": self.color.value,
            },
        }


@dataclass
class Heading(NotionBlock, RichTextsBlock):
    color: RichColor
    is_toggleable: bool

    def __init__(
        self,
        header_type: Literal[
            BlockType.HEADER_1, BlockType.HEADER_2, BlockType.HEADER_3
        ],
        rich_texts: list[RichText] | None = None,
        color: RichColor = RichColor.DEFAULT,
        is_toggleable: bool = False,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(header_type, block_id, parent)
        RichTextsBlock.__init__(self, rich_texts)
        self.color = color
        self.is_toggleable = is_toggleable

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                **RichTextsBlock.to_dict(self),
                "color": self.color.value,
                "toggleable": self.is_toggleable,
            },
        }


@dataclass
class Code(NotionBlock, RichTextsBlock):
    captions: list[RichText]
    language: LanguageType

    def __init__(
        self,
        language: LanguageType,
        captions: list[RichText] | None = None,
        rich_texts: list[RichText] | None = None,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.CODE, block_id, parent)
        RichTextsBlock.__init__(self, rich_texts)
        self.captions = captions or []
        self.language = language

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                **RichTextsBlock.to_dict(self),
                "language": self.language.value,
                "caption": [c.to_dict() for c in self.captions],
            },
        }


@dataclass
class ListItem(NotionBlock, RichTextsBlock, HierarchicalBlock):
    color: RichColor

    def __init__(
        self,
        list_type: Literal[BlockType.BULLETED_LIST_ITEM, BlockType.NUMBERED_LIST_ITEM],
        rich_texts: list[RichText],
        color: RichColor = RichColor.DEFAULT,
        children: list[NotionBlock] | None = None,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(list_type, block_id, parent)
        RichTextsBlock.__init__(self, rich_texts)
        HierarchicalBlock.__init__(self, children)
        self.color = color

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                **RichTextsBlock.to_dict(self),
                **HierarchicalBlock.to_dict(self),
                "color": self.color.value,
            },
        }


@dataclass
class Callout(NotionBlock, RichTextsBlock):
    color: RichColor
    icon: NotionEmoji | None

    def __init__(
        self,
        rich_texts: list[RichText] | None = None,
        icon: NotionEmoji | None = None,
        color: RichColor = RichColor.DEFAULT,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.CALLOUT, block_id, parent)
        RichTextsBlock.__init__(self, rich_texts)
        self.color = color
        self.icon = icon or None

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                **RichTextsBlock.to_dict(self),
                "color": self.color.value,
                "icon": self.icon.to_dict() if self.icon else None,
            },
        }


@dataclass
class Divider(NotionBlock):
    def __init__(
        self,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.DIVIDER, block_id, parent)


@dataclass
class Table(NotionBlock):
    table_width: int
    has_column_header: bool
    has_row_header: bool

    def __init__(
        self,
        table_width: int,
        has_column_header: bool = False,
        has_row_header: bool = False,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.TABLE, block_id, parent)
        self.table_width = table_width
        self.has_column_header = has_column_header
        self.has_row_header = has_row_header

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                "table_width": self.table_width,
                "has_column_header": self.has_column_header,
                "has_row_header": self.has_row_header,
            },
        }


@dataclass
class TableRow(NotionBlock):
    cells: list[RichText]

    def __init__(
        self,
        cells: list[RichText] | None = None,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.TABLE_ROW, block_id, parent)
        self.cells = cells or []

    def add_cell(self, cell: RichText):
        self.cells.append(cell)

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                "cells": [c.to_dict() for c in self.cells],
            },
        }


@dataclass
class Image(NotionBlock):
    file: NotionFile

    def __init__(
        self,
        file: NotionFile,
        block_id: uuid.UUID | None = None,
        parent: NotionParent | None = None,
    ):
        super().__init__(BlockType.IMAGE, block_id, parent)
        self.file = file

    def to_dict(self) -> dict:
        return {
            **super().to_dict(),
            self.type.value: {
                **self.file.to_dict(),
            },
        }
