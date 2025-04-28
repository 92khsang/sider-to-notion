from __future__ import annotations as _annotations

import logging
from collections import deque
from typing import TYPE_CHECKING, Optional, Union, Iterable

from pydantic import ValidationError
from pynotion.models import (
    Annotations,
    NotionUrlWrapper,
    Text,
    TxTextRichText,
)

from sider_to_notion.extractor import TagElement, NavStringElement

if TYPE_CHECKING:
    from pynotion.models import TxRichText

RICH_TEXT_TAGS = ["p", "a", "code", "span"]


def create_tx_rich_text(text: str) -> TxTextRichText:
    return TxTextRichText(text=Text(content=text))


def convert_nav_string_to_rich_text(nav_string: NavStringElement) -> TxTextRichText:
    text = nav_string.text()
    text = text.replace("\n", " ")
    return create_tx_rich_text(text)


def extract_content_and_title(
    tag: TagElement,
) -> tuple[Optional[TagElement], Optional[TagElement]]:
    content_element: Optional[TagElement] = None
    title_element: Optional[TagElement] = None

    while tag.children:
        child = tag.children.popleft()
        if child.classification == "content":
            content_element = child
        if child.classification == "title":
            title_element = child

    return content_element, title_element


def search_child_by_classification(
    tag: TagElement, classification: Union[str, Iterable[str]]
) -> deque[TagElement]:
    found_children: deque[TagElement] = deque()

    if isinstance(classification, str):
        classification = [classification]

    while tag.children:
        child = tag.children.popleft()
        if isinstance(child, TagElement) and child.classification in classification:
            found_children.append(child)

    return found_children


def extract_tags_from_children(tag: TagElement) -> list[TagElement]:
    tags: list[TagElement] = []
    while tag.children:
        child = tag.children.popleft()
        if isinstance(child, TagElement):
            tags.append(child)
    return tags


def is_convertible(tag: TagElement) -> bool:
    return tag.classification in RICH_TEXT_TAGS


def _extract_rich_texts(child) -> list[TxTextRichText]:
    if isinstance(child, NavStringElement):
        if child.text(True) == "":
            return []

        rich_texts = [convert_nav_string_to_rich_text(child)]
    else:
        rich_texts = convert_to_rich_texts(child)

    return rich_texts


def _convert_link_rich_texts(tag: TagElement) -> list[TxRichText]:
    if tag.tag_name != "a":
        raise ValueError(f"Expected a, got {tag.tag_name}")

    rich_texts = []

    while tag.children:
        child = tag.children.popleft()
        rich_texts.extend(_extract_rich_texts(child))

    try:
        for rich_text in rich_texts:
            rich_text.text.link = NotionUrlWrapper(url=tag.attrs.get("href"))
    except ValidationError as e:
        logging.debug("Failed to convert a link: %s", e)

    return rich_texts


def _convert_code_rich_texts(tag: TagElement) -> list[TxRichText]:
    if tag.tag_name != "code":
        raise ValueError(f"Expected code, got {tag.tag_name}")

    rich_texts = []

    while tag.children:
        child = tag.children.popleft()
        rich_texts.extend(_extract_rich_texts(child))

    for rich_text in rich_texts:
        rich_text.annotations = (
            rich_text.annotations if rich_text.annotations else Annotations()
        )
        rich_text.annotations.code = True

    return rich_texts


def _jump_to_next_rich_texts(tag: TagElement) -> list[TxRichText]:
    rich_texts = []

    while tag.children:
        child = tag.children.popleft()
        rich_texts.extend(_extract_rich_texts(child))

    return rich_texts


def convert_to_rich_texts(tag: TagElement) -> list[TxRichText]:
    match tag.classification:
        case "a":
            return _convert_link_rich_texts(tag)
        case "code":
            return _convert_code_rich_texts(tag)
        case _:
            return _jump_to_next_rich_texts(tag)
