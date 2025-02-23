from __future__ import annotations

import os
from dataclasses import dataclass, field

from dotenv import load_dotenv

from app.core.log import get_logger

_logger = get_logger(__name__)


@dataclass(frozen=True, slots=True)
class Settings:
    NOTION_API_TOKEN: str = field(init=False)
    NOTION_DATABASE_ID: str = field(init=False)

    def __post_init__(self):
        object.__setattr__(self, "NOTION_API_TOKEN", os.getenv("NOTION_API_TOKEN"))
        object.__setattr__(self, "NOTION_DATABASE_ID", os.getenv("NOTION_DATABASE_ID"))

        if not self.NOTION_API_TOKEN or not self.NOTION_DATABASE_ID:
            raise ValueError("NOTION_API_TOKEN or NOTION_DATABASE_ID not found in .env")


try:
    load_dotenv()
    settings = Settings()
except ValueError as e:
    _logger.error(f"Configuration Error: {e}")
    exit(1)

NOTION_HEADERS = {
    "Authorization": f"Bearer {settings.NOTION_API_TOKEN}",
    "Content-Type": "application/json",
    "Notion-Version": "2021-08-16",
}
