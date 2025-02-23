from __future__ import annotations

from copy import copy
from typing import (
    TYPE_CHECKING,
    override,
)

from app.extract.base import DocExtractor
from app.extract.spring.tags import SPRING_TAG_EXTRACTORS

if TYPE_CHECKING:
    from bs4 import (
        BeautifulSoup,
        Tag,
    )
    from app.extract.base import TagExtractor


class SpringDocDocExtractor(DocExtractor):

    def __init__(self, soup: BeautifulSoup):
        super().__init__(soup)

    @override
    @property
    def root_tag(self) -> Tag:
        return copy(self.soup.find("article", attrs={"class": "doc"}))

    @override
    @property
    def extractors(self) -> list[TagExtractor]:
        return SPRING_TAG_EXTRACTORS
