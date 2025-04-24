from __future__ import annotations

from dataclasses import dataclass, field
from functools import cache
from typing import TYPE_CHECKING

from sider_to_notion.core.decorators import singleton
from sider_to_notion.sites.base import DocProcessor

if TYPE_CHECKING:
    from sider_to_notion.sites.models import DocType


@singleton
@dataclass
class DocRegistry:
    processors: dict[DocType, DocProcessor] = field(default_factory=dict)

    @staticmethod
    @cache
    def _load_processors(doc_type: DocType) -> None:
        import importlib

        importlib.import_module(f"{__spec__.parent}.{doc_type.lower()}")  # noqa

    def fetch(self, doc_type: DocType) -> DocProcessor:
        if doc_type not in self.processors:
            self._load_processors(doc_type)

        processor = self.processors.get(doc_type)
        if processor is None:
            raise RuntimeError(f"Processor for {doc_type} was not registered")
        return processor

    def register(self, doc_type: DocType, processor: DocProcessor) -> None:
        if doc_type in self.processors:
            return

        self.processors[doc_type] = processor
