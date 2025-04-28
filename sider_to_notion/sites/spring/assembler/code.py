from __future__ import annotations as _annotations

from typing import TYPE_CHECKING

from pynotion.models import (
    ProgrammingLanguage,
    TxCode,
    TxCodeBlock,
)

from sider_to_notion.extractor import TagElement, NavStringElement
from sider_to_notion.sites.models import BlockTree
from ._registry import register
from ._utils import create_tx_rich_text

if TYPE_CHECKING:
    pass


def _parse_code_txt(inner_tag: TagElement, texts: list[str]) -> None:
    while inner_tag.children:
        child = inner_tag.children.popleft()
        if isinstance(child, NavStringElement):
            texts.append(str(child.element))
        else:
            _parse_code_txt(child, texts)


def _split_text(text: str, max_length: int = 999) -> list[str]:
    """Split text into chunks of at most max_length characters."""
    return [text[i : i + max_length] for i in range(0, len(text), max_length)]


def convert_code_block_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    try:
        lang = ProgrammingLanguage(tag.attrs["data-lang"])
    except (KeyError, ValueError):
        lang = ProgrammingLanguage.PLAIN_TEXT

    texts: list[str] = []
    _parse_code_txt(tag, texts)

    full_text = "".join(texts)
    chunks = _split_text(full_text)

    code_block = TxCodeBlock(
        code=TxCode(
            rich_text=[create_tx_rich_text(chunk) for chunk in chunks],
            language=lang,
        )
    )

    code_node = BlockTree(parent, code_block)
    return [code_node]


register("code_block", convert_code_block_to_node)
