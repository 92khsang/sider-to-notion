from __future__ import annotations

from typing import Final, Type

from bs4 import BeautifulSoup

from app.converters.base import DocConverter
from app.converters.models import Element
from app.converters.spring import SpringDocDocConverter
from app.core.types import DocType


class ConvertError(Exception):
    pass


DOC_CONVERT_MAP: Final[dict[DocType, Type[DocConverter]]] = {
    DocType.SPRING: SpringDocDocConverter
}


def convert_doc_to_element(doc: DocType, soup: BeautifulSoup) -> Element:
    if doc not in DOC_CONVERT_MAP:
        raise NotImplementedError(f"{doc} is not supported")
    return DOC_CONVERT_MAP[doc](soup).convert()


__all__ = ["convert_doc_to_element"]
