from __future__ import annotations

from pathlib import Path
from typing import Final

from bs4 import BeautifulSoup

from app.core.types import DocType
from app.downloaders.base import Downloader
from app.downloaders.spring import SpringDocDownloader
from app.downloaders.utils import request_html

DOC_DOWNLOADER_MAP: Final[dict[DocType, Downloader]] = {
    DocType.SPRING: SpringDocDownloader(),
}


def download_html(
    doc: DocType, url: str, downloaded_html: Path | None = None
) -> BeautifulSoup:
    if doc not in DOC_DOWNLOADER_MAP:
        raise NotImplementedError(f"{doc} is not supported")

    return DOC_DOWNLOADER_MAP[doc].download_html(url, downloaded_html)


__all__ = ["download_html"]
