from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Optional

from sider_to_notion.core.decorators import singleton

if TYPE_CHECKING:
    from bs4 import BeautifulSoup
    from sider_to_notion.extractor.model import TagElement
    from sider_to_notion.sites.models import Doc, BlockTree


@singleton
class DocProcessor(metaclass=ABCMeta):
    def process(self, doc: "Doc") -> "BlockTree":
        html_soup = self.read(doc.url, doc.html_str)
        element = self.extract(html_soup)
        return self.assemble(element)

    @abstractmethod
    def read(self, url: str, html_str: Optional[str] = None) -> "BeautifulSoup": ...

    @abstractmethod
    def extract(self, html_soup: "BeautifulSoup") -> "TagElement": ...

    @abstractmethod
    def assemble(self, element: "TagElement") -> "BlockTree": ...
