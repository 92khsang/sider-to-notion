from __future__ import annotations

from abc import abstractmethod, ABCMeta
from typing import TYPE_CHECKING

from app.notion.models import NotionBlock, RichText
from app.notion.types import BlockType

if TYPE_CHECKING:
    from app.extractor.models import TagElement


class Renderer(metaclass=ABCMeta):
    _instances: dict[type, Renderer] = {}

    def __new__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__new__(cls)
        return cls._instances[cls]

    @abstractmethod
    def is_renderable(self, element: TagElement) -> bool: ...

    @abstractmethod
    def render(self, element: TagElement) -> NotionBlock: ...


class HTagRenderer(Renderer):
    def is_renderable(self, element: TagElement) -> bool:
        return element.tag_name in ["h1", "h2", "h3", "h4", "h5", "h6"]

    def render(self, element: TagElement) -> NotionBlock:
        h_level = min(int(element.tag_name[1:]), 3)

        from app.notion.models.blocks import Heading

        return Heading(
            header_type=BlockType.from_value(f"header_{h_level}"),
            rich_texts=[RichText(element.text(strip=True))],
            block_id=element.id,
        )


__all__ = ["Renderer", "HTagRenderer"]
