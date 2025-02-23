from __future__ import annotations

from dataclasses import dataclass

from app.notion.types import RichColor


@dataclass
class Text:
    content: str
    link: str | None = None

    def to_dict(self) -> dict:
        return {
            "content": self.content,
            **({"link": {"url": self.link}} if self.link else {}),
        }


@dataclass
class Annotations:
    bold: bool = False
    italic: bool = False
    strikethrough: bool = False
    underline: bool = False
    code: bool = False
    color: RichColor = RichColor.DEFAULT

    def to_dict(self) -> dict:
        return {
            "bold": self.bold,
            "italic": self.italic,
            "strikethrough": self.strikethrough,
            "underline": self.underline,
            "code": self.code,
            "color": self.color.value,
        }


@dataclass
class RichText:
    plain_text: str
    text: Text
    annotations: Annotations
    href: str | None = None

    def __init__(
        self,
        text: str,
        link: str | None = None,
        annotations_: Annotations | None = None,
    ):
        self.plain_text = text
        self.text = Text(text, link)
        self.annotations = annotations_ or Annotations()
        self.href = link

    def to_dict(self) -> dict:
        return {
            "type": "text",
            "text": self.text.to_dict(),
            "annotations": self.annotations.to_dict(),
            **({"href": self.href} if self.href else {}),
        }
