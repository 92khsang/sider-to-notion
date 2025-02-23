from __future__ import annotations

from typing import NamedTuple, Literal

from app.notion.models import NotionId


class CustomEmoji(NamedTuple):
    name: str
    url: str
    id: NotionId | None = None

    def to_dict(self):
        return {
            "name": self.name,
            "url": self.url,
            **({"id": str(self.id)} if self.id else {}),
        }


class NotionEmoji(NamedTuple):
    type: Literal["emoji", "custom_emoji"]
    emoji: str | CustomEmoji

    def to_dict(self):
        return {
            "type": self.type,
            "emoji": (
                self.emoji.to_dict()
                if isinstance(self.emoji, CustomEmoji)
                else self.emoji
            ),
        }
