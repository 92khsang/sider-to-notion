from __future__ import annotations

from collections import defaultdict
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from bs4 import Tag


def extract_translation(tag: Tag) -> str:
    return tag.find("sider-trans-text").text.strip()


def decompose_translation(tag: Tag) -> None:
    element = tag.find("sider-trans")
    if element:
        element.decompose()


def extract_attrs(tag: Tag) -> dict[str, list[str]]:
    attrs = tag.attrs
    extracted_attrs = defaultdict(list)
    for key, value in attrs.items():
        if isinstance(value, str):
            extracted_attrs[key].append(value)
        else:
            extracted_attrs[key].extend(value)

    return extracted_attrs
