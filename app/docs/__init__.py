from __future__ import annotations

from abc import ABCMeta, abstractmethod
from dataclasses import dataclass, field
from enum import StrEnum
from typing import TYPE_CHECKING

from app.core.decorators import singleton
from app.extractor.models import Element

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from app.notion.models import NotionProperty, NotionBlock


class DocType(StrEnum):
    SPRING = "spring"


@dataclass(frozen=True, slots=True)
class Doc:
    type: DocType
    url: str
    html_str: str | None = field(default=None)
    properties: set[NotionProperty] = field(default_factory=lambda: set())


@singleton
class DocProcessor(metaclass=ABCMeta):

    def process(self, doc: Doc) -> None:
        html_soup = self.read(doc.url, doc.html_str)
        element = self.extract(html_soup)
        blocks = self.render(element)
        self.write(blocks, doc.properties)

    @abstractmethod
    def read(self, url: str, html_str: str | None = None) -> BeautifulSoup: ...

    @abstractmethod
    def extract(self, html_soup: BeautifulSoup) -> Element: ...

    @abstractmethod
    def render(self, element: Element) -> list[NotionBlock]: ...

    @abstractmethod
    def write(
        self, blocks: list[NotionBlock], properties: set[NotionProperty]
    ) -> None: ...


DOC_PROCESSORS: dict[DocType, DocProcessor] = {}


def _load_module(doc: DocType) -> None:
    import importlib

    importlib.import_module(f"app.docs.{doc.lower()}")


def add_processor(doc_type: DocType, processor: DocProcessor) -> None:
    if doc_type in DOC_PROCESSORS:
        return

    DOC_PROCESSORS[doc_type] = processor


def get_processor(doc_type: DocType) -> DocProcessor:
    if doc_type not in DocType:
        raise NotImplementedError(f"{doc_type} is not supported")
    if doc_type not in DOC_PROCESSORS:
        _load_module(doc_type)

    return DOC_PROCESSORS[doc_type]


def run_processor(doc: Doc) -> None:
    if doc.type not in DocType:
        raise NotImplementedError(f"{doc} is not supported")
    return get_processor(doc.type).process(doc)


__all__ = [
    "add_processor",
    "get_processor",
    "run_processor",
    "DocProcessor",
    "DocType",
    "Doc",
]
