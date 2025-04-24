from __future__ import annotations as _annotations

from typing import TYPE_CHECKING

from pynotion.models import (
    ExternalFile,
    ExternalFileObject,
    TxImageBlock,
)

from sider_to_notion.sites.models import BlockTree
from ._registry import register
from ._utils import extract_content_and_title

if TYPE_CHECKING:
    from sider_to_notion.extractor import TagElement


def convert_image_block_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    image_element, title_element = extract_content_and_title(tag)

    if image_element is None:
        raise ValueError("No image found")

    image_block = TxImageBlock(
        image=ExternalFile(
            external=ExternalFileObject(url=image_element.children[0].attrs.get("src"))
        )
    )

    if title_element:
        from .text import convert_text_with_trans_to_block

        title_block, _ = convert_text_with_trans_to_block(title_element, "toggle")
        block_node = BlockTree(parent, title_block)
        block_node.add_child_block(image_block)
    else:
        block_node = BlockTree(parent, image_block)

    return [block_node]


def convert_block_classification_to_node(
    parent: BlockTree, tag: TagElement
) -> list[BlockTree]:
    content_element, title_element = extract_content_and_title(tag)

    if content_element is None:
        raise ValueError("No content found")

    from ._registry import CONVERTERS

    block_nodes = []

    while content_element.children:
        content_item_element = content_element.children.popleft()
        content_nodes: list[BlockTree] = CONVERTERS[
            content_item_element.classification
        ](parent, content_item_element)

        if title_element:
            from .text import convert_text_with_trans_to_block

            title_block, _ = convert_text_with_trans_to_block(title_element, "toggle")

            title_node = BlockTree(parent, title_block)
            title_node.add_child_nodes(content_nodes)

            block_nodes.append(title_node)
        else:
            block_nodes.extend(content_nodes)

    return block_nodes


register("imageblock", convert_image_block_to_node)
register("listingblock", convert_block_classification_to_node)
register("exampleblock", convert_block_classification_to_node)
