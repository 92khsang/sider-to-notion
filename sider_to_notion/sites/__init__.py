from __future__ import annotations

from typing import TYPE_CHECKING

from sider_to_notion.sites.base import DocProcessor
from sider_to_notion.sites.models import Doc, DocType, BlockTree
from sider_to_notion.sites.registry import DocRegistry

registry = DocRegistry()

__all__ = [
    "registry",
    "DocType",
    "BlockTree",
    "Doc",
]

if TYPE_CHECKING:
    __all__ += [
        "DocProcessor",
    ]
