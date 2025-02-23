from __future__ import annotations

from typing import Final

from bs4 import BeautifulSoup

from app.core.types import DocType
from app.download.base import Downloader
from app.download.spring import SpringDocDownloader
from app.download.utils import request_html

DOC_DOWNLOADER_MAP: Final[dict[DocType, Downloader]] = {
    DocType.SPRING: SpringDocDownloader(),
}


def download_html(
    doc: DocType, url: str, downloaded_html: str | None = None
) -> BeautifulSoup:
    """
    Downloads the HTML page from the given URL and parses it into a `BeautifulSoup`
    object.

    If `downloaded_html` is given, it is used instead of downloading the HTML from
    the URL.

    A `NotImplementedError` is raised if the given `doc` is not supported.

    Parameters
    ----------
    doc : DocType
        The type of documentation to download.
    url : str
        The URL of the page to download.
    downloaded_html : str | None, optional
        The downloaded HTML content.
        Defaults to None, which means the HTML is
        downloaded from the URL.

    Returns
    -------
    BeautifulSoup
        The parsed HTML page.
    """
    if doc not in DOC_DOWNLOADER_MAP:
        raise NotImplementedError(f"{doc} is not supported")

    return DOC_DOWNLOADER_MAP[doc].download_html(url, downloaded_html)


__all__ = ["download_html"]
