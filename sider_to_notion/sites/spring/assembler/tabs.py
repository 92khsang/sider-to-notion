from __future__ import annotations as _annotations

from pynotion.models import (
    TxToggle,
    TxToggleBlock,
)

from sider_to_notion.extractor import TagElement
from sider_to_notion.sites.models import BlockTree
from ._registry import register
from ._utils import extract_content_and_title, create_tx_rich_text
from .block import convert_block_classification_to_node
from .text import convert_text_with_trans_to_block, convert_list_to_node


def convert_tabs_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    content_element, title_element = extract_content_and_title(tag)

    if content_element is None:
        raise ValueError("No content found")

    if title_element:
        tab_block, _ = convert_text_with_trans_to_block(title_element, "toggle")
    else:
        tab_block = TxToggleBlock(
            toggle=TxToggle(rich_text=[create_tx_rich_text("Tabs")])
        )

    tab_node = BlockTree(parent, tab_block)

    tab_list_element: TagElement = content_element.children.popleft()
    if tab_list_element.classification != "tablist":
        raise ValueError(f"Expected tablist, but got {tab_list_element.classification}")

    ul_element = tab_list_element.children.popleft()
    if ul_element.classification != "ul":
        raise ValueError(f"Expected ul, but got {ul_element.classification}")
    tab_list_nodes: list[BlockTree] = convert_list_to_node(tab_node, ul_element)

    for tab_list_node in tab_list_nodes:
        child = content_element.children.popleft()
        if isinstance(child, TagElement) and child.classification == "listingblock":
            converted_node = convert_block_classification_to_node(tab_list_node, child)
            tab_list_node.add_child_nodes(converted_node)

    if content_element.children:
        raise ValueError(
            "The number of tab lists and the number of tab contents do not match."
        )

    tab_node.add_child_nodes(tab_list_nodes)
    return [tab_node]


register("tabs", convert_tabs_node)
