from typing import override, TYPE_CHECKING

from bs4 import BeautifulSoup

from sider_to_notion.extractor.model import TagElement
from sider_to_notion.fetcher import ExcludeTags, ExcludeTag
from sider_to_notion.sites import registry as docs_registry
from sider_to_notion.sites.base import DocProcessor
from sider_to_notion.sites.models import DocType

if TYPE_CHECKING:
    from sider_to_notion.sites.base import DatabaseParent, DocProperties, BlockTree


EXCLUDE_TAGS: ExcludeTags = ExcludeTags(
    tags=[
        ExcludeTag(tag="div", attrs={"class": {"breadcrumbs-container"}}),
        ExcludeTag(tag="div", attrs={"class": {"nav-container"}}),
        ExcludeTag(tag="div", attrs={"class": {"toolbar"}}),
        ExcludeTag(tag="div", attrs={"class": {"modal"}}),
        ExcludeTag(tag="header", attrs={"class": {"header"}}),
        ExcludeTag(tag="footer", attrs={"class": {"footer"}}),
        ExcludeTag(tag="aside", attrs={"class": {"sidebar"}}),
        ExcludeTag(tag="aside", attrs={"class": {"toc", "embedded"}}),
        ExcludeTag(tag="span", attrs={"class": {"copy-toast"}}),
        ExcludeTag(tag="script", attrs={}),
        ExcludeTag(tag="a", attrs={"class": {"anchor"}}),
        ExcludeTag(tag="chatgpt-sidebar", attrs={}),
        ExcludeTag(tag="chatgpt-sidebar-popups", attrs={}),
        ExcludeTag(tag="button", attrs={"class": {"copy-button"}}),
    ]
)


class SpringDocProcessor(DocProcessor):

    @override
    def read(self, url: str, html_str: str | None = None) -> BeautifulSoup:
        from sider_to_notion.fetcher import fetch_html

        return fetch_html(EXCLUDE_TAGS, url, html_str)

    @override
    def extract(self, html_soup: BeautifulSoup) -> TagElement:
        from sider_to_notion.extractor import extract_to_element
        from .extractor import tag_extractors, root_tag

        return extract_to_element(tag_extractors(), root_tag(html_soup))

    @override
    def assemble(self, element: "TagElement") -> "BlockTree":
        from .assembler import assemble

        return assemble(element)


docs_registry.register(DocType.SPRING, SpringDocProcessor())

__all__ = []
