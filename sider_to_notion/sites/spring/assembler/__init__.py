import logging
from typing import TYPE_CHECKING

from sider_to_notion.sites import BlockTree
from ._registry import CONVERTERS

if TYPE_CHECKING:
    from sider_to_notion.extractor import TagElement


def _is_convertible(tag: "TagElement") -> bool:
    return tag.classification in CONVERTERS


def _convert(parent: BlockTree, tag: "TagElement") -> list[BlockTree]:
    if not _is_convertible(tag):
        logging.error(f"Unknown block tag {tag.tag_name} {tag.classification}")

    return CONVERTERS[tag.classification](parent, tag)


def assemble(tag: "TagElement") -> BlockTree:
    root_node = BlockTree()

    while tag.children:
        child = tag.children.popleft()
        blocks = _convert(root_node, child)
        root_node.add_child_nodes(blocks)

    return root_node
