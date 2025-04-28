from __future__ import annotations as _annotations

from typing import TYPE_CHECKING

from pynotion.models import (
    TxDividerBlock,
)

from sider_to_notion.sites.models import BlockTree
from ._registry import register
from ._utils import search_child_by_classification
from .text import convert_text_with_trans_to_block

if TYPE_CHECKING:
    from sider_to_notion.extractor import TagElement


def convert_footnotes_to_node(parent: BlockTree, tag: "TagElement") -> list[BlockTree]:
    blocks = []

    divider_block = TxDividerBlock()
    blocks.append(BlockTree(parent, divider_block))

    footnote_elements = search_child_by_classification(tag, "footnote")
    if len(footnote_elements) == 0:
        raise ValueError("No footnote elements are found in the provided tag.")

    while footnote_elements:
        footnote_element = footnote_elements.popleft()
        footnote_block, trans_block = convert_text_with_trans_to_block(
            footnote_element, "paragraph"
        )
        footnote_node = BlockTree(parent, footnote_block)
        if trans_block:
            footnote_node.add_child_block(trans_block)

        blocks.append(footnote_node)

    return blocks


register("footnotes", convert_footnotes_to_node)
