from __future__ import annotations

from typing import Final, Type

from bs4 import BeautifulSoup

from app.core.types import DocType
from app.extract.base import DocExtractor
from app.extract.models import Element
from app.extract.spring import SpringDocDocExtractor


class ExtractError(Exception):
    pass


DOC_EXTRACT_MAP: Final[dict[DocType, Type[DocExtractor]]] = {
    DocType.SPRING: SpringDocDocExtractor
}


def extract_element(doc: DocType, soup: BeautifulSoup) -> Element:
    if doc not in DOC_EXTRACT_MAP:
        raise NotImplementedError(f"{doc} is not supported")
    return DOC_EXTRACT_MAP[doc](soup).extract()


__all__ = ["extract_element"]
