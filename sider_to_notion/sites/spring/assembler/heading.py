from __future__ import annotations as _annotations

from typing import TYPE_CHECKING

from pynotion.models import (
    TxHeading,
    TxHeadingOneBlock,
    TxHeadingThreeBlock,
    TxHeadingTwoBlock,
)

from sider_to_notion.sites.models import BlockTree
from ._registry import register
from ._utils import create_tx_rich_text

if TYPE_CHECKING:
    from sider_to_notion.extractor import TagElement, NavStringElement


def convert_heading_to_node(parent: BlockTree, h_tag: "TagElement") -> list[BlockTree]:
    H_TAG_MAP = {
        "h1": (TxHeadingOneBlock, "heading_1"),
        "h2": (TxHeadingTwoBlock, "heading_2"),
    }

    tag_clz, attr_name = (TxHeadingThreeBlock, "heading_3")

    h_tag_name: str = h_tag.tag_name
    if h_tag_name in H_TAG_MAP:
        tag_clz, attr_name = H_TAG_MAP[h_tag_name]

    h_txt: NavStringElement = h_tag.children.popleft()
    h_tag_level = int(h_tag_name[1:])

    is_toggleable = h_tag_level in [2, 3, 4]
    block = tag_clz(
        **{
            attr_name: TxHeading(
                is_toggleable=is_toggleable,
                rich_text=[create_tx_rich_text(h_txt.text(True))],
            )
        }
    )

    block_node = BlockTree(parent, block)
    return [block_node]


register("heading", convert_heading_to_node)
