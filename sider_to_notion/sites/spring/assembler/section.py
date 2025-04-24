from pynotion.models import (
    TxHeading,
    TxHeadingThreeBlock,
    TxHeadingTwoBlock,
)

from sider_to_notion.extractor import TagElement
from sider_to_notion.sites.models import BlockTree
from ._registry import register
from ._utils import create_tx_rich_text


def convert_section_to_node(parent: BlockTree, tag: "TagElement") -> list[BlockTree]:
    section_number = int(tag.classification[-1:])
    if (
        hasattr(tag.children[0], "classification")
        and tag.children[0].classification == "heading"
    ):
        from .heading import convert_heading_to_node

        h_child = tag.children.popleft()
        section_node = convert_heading_to_node(parent, h_child)[0]
    else:
        h_tag_number = section_number + 1
        heading_block_clz = (
            TxHeadingTwoBlock if h_tag_number == 2 else TxHeadingThreeBlock
        )

        h_block = heading_block_clz(
            **{
                f"heading_{h_tag_number}": TxHeading(
                    rich_text=[create_tx_rich_text("Empty (Section One)")],
                    is_toggleable=True,
                )
            }
        )
        section_node = BlockTree(parent, h_block)

    from ._registry import CONVERTERS

    while tag.children:
        child = tag.children.popleft()
        if isinstance(child, TagElement):
            child_nodes = CONVERTERS[child.classification](section_node, child)
            for child_node in child_nodes:
                section_node.add_child_node(child_node)

    return [section_node]


register("sect1", convert_section_to_node)
register("sect2", convert_section_to_node)
register("sect3", convert_section_to_node)
register("sect4", convert_section_to_node)
