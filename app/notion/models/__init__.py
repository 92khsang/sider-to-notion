from __future__ import annotations

import uuid
from typing import NamedTuple, TypeAlias, Literal

from app.notion.models.blocks import NotionBlock
from app.notion.models.emoji import NotionEmoji
from app.notion.models.properties import NotionProperty
from app.notion.models.rich_text import RichText
from app.notion.types import ParentType

NotionId: TypeAlias = uuid.UUID


class NotionFile(NamedTuple):
    type: Literal["file", "external"]
    url: str
    expiry_time: str | None

    def to_dict(self) -> dict[str, str]:
        return {
            "type": self.type,
            "url": self.url,
            **({"expiry_time": self.expiry_time} if self.expiry_time else {}),
        }


class NotionParent(NamedTuple):
    type: ParentType
    nid: NotionId

    def to_dict(self) -> dict[str, str]:
        return {"type": self.type.value, self.type.value: str(self.nid)}


class NotionPage(NamedTuple):
    properties: set[NotionProperty]
    blocks: list[NotionBlock] = []

    def add_block(self, block: NotionBlock) -> None:
        self.blocks.append(block)


__all__ = [
    "blocks",
    "rich_text",
    "properties",
    "emoji",
    "NotionId",
    "NotionEmoji",
    "NotionFile",
    "NotionPage",
    "NotionProperty",
    "NotionParent",
    "NotionBlock",
    "RichText",
]
