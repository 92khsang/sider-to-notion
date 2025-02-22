from __future__ import annotations

from copy import copy
from typing import (
    TYPE_CHECKING,
    override,
)

from app.converters.base import DocConverter
from app.converters.spring.tags import SPRING_TAG_CONVERTERS

if TYPE_CHECKING:
    from bs4 import (
        BeautifulSoup,
        Tag,
    )
    from app.converters.base import TagConverter


class SpringDocDocConverter(DocConverter):

    def __init__(self, soup: BeautifulSoup):
        super().__init__(soup)

    @override
    @property
    def root_tag(self) -> Tag:
        return copy(self.soup.find("article", attrs={"class": "doc"}))

    @override
    @property
    def converters(self) -> list[TagConverter]:
        return SPRING_TAG_CONVERTERS
