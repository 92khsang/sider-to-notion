from __future__ import annotations as _annotations

from collections import deque
from typing import TYPE_CHECKING, Optional, Literal, Union

from pynotion.models import (
    Color,
    TxBulletListItem,
    TxBulletListItemBlock,
    TxNumberedListItem,
    TxNumberedListItemBlock,
    TxParagraph,
    TxParagraphBlock,
    TxTextRichText,
    TxToggle,
    TxToggleBlock,
)

from sider_to_notion.extractor import TagElement
from sider_to_notion.sites.models import BlockTree
from ._registry import CONVERTERS, register
from ._utils import (
    convert_to_rich_texts,
    search_child_by_classification,
    RICH_TEXT_TAGS,
)

if TYPE_CHECKING:
    from pynotion.models import TxRichText, TxBlock

TextBlockType = Literal[
    "paragraph", "bulleted_list_item", "numbered_list_item", "toggle"
]
TextBlockUnion = Union[
    TxParagraphBlock, TxBulletListItemBlock, TxNumberedListItemBlock, TxToggleBlock
]

BLOCK_TYPE_CLASS_MAP: dict[TextBlockType, tuple[type[TxBlock], type]] = {
    "paragraph": (TxParagraphBlock, TxParagraph),
    "bulleted_list_item": (TxBulletListItemBlock, TxBulletListItem),
    "numbered_list_item": (TxNumberedListItemBlock, TxNumberedListItem),
    "toggle": (TxToggleBlock, TxToggle),
}

CLASSIFICATION_TO_BLOCK_TYPE: dict[str, TextBlockType] = {
    "paragraph": "paragraph",
    "ulist": "bulleted_list_item",
    "olist": "numbered_list_item",
    "toggle": "toggle",
}

LIST_TAG_CLASSIFICATION_TO_BLOCK_TYPE: dict[str, TextBlockType] = {
    "ul": "bulleted_list_item",
    "ol": "numbered_list_item",
}


def _has_enough_translation_length(block: TxParagraphBlock) -> bool:
    texts = [
        rt.text.content
        for rt in block.paragraph.rich_text
        if isinstance(rt, TxTextRichText)
    ]
    joined = "".join(texts)
    return joined.count(" ") > 1 and len(joined) > 10


def _extract_translation_text(p_tag: TagElement) -> Optional[TagElement]:
    for child in p_tag.children:
        if getattr(child, "tag_name", None) == "sider-trans-text":
            p_tag.children.remove(child)
            return child
    return None


def convert_text_to_block(
    tag: TagElement,
    children: Optional[list[TxBlock]] = None,
    block_type: TextBlockType = "bulleted_list_item",
) -> TextBlockUnion:
    block_cls, item_cls = BLOCK_TYPE_CLASS_MAP[block_type]
    rich_text: list[TxRichText] = convert_to_rich_texts(tag)
    return block_cls(**{block_type: item_cls(rich_text=rich_text, children=children)})


def convert_text_with_trans_to_block(
    tag: TagElement, block_type: TextBlockType
) -> tuple[TextBlockUnion, Optional[TxParagraphBlock]]:
    trans_block: Optional[TxParagraphBlock] = None
    trans_tag = _extract_translation_text(tag)

    block = convert_text_to_block(tag, block_type=block_type)
    if trans_tag:
        temp_trans_block = convert_text_to_block(trans_tag, block_type="paragraph")
        if _has_enough_translation_length(temp_trans_block):
            temp_trans_block.paragraph.color = Color.GRAY
            trans_block = temp_trans_block

    return block, trans_block


def convert_list_item_to_node(
    parent: BlockTree, list_items: deque[TagElement], block_type: TextBlockType
) -> list[BlockTree]:
    list_item_nodes: list[BlockTree] = []

    while list_items:
        list_item: TagElement = list_items.popleft()

        text_tags = [
            child
            for child in list_item.children
            if child.classification in RICH_TEXT_TAGS
        ]

        if len(text_tags) != 1:
            raise ValueError(f"Expected 1 rich text tag, but got {len(text_tags)}")

        text_tag = text_tags[0]
        list_item.children.remove(text_tag)

        text_block, trans_block = convert_text_with_trans_to_block(text_tag, block_type)

        list_item_node = BlockTree(parent, text_block)
        if trans_block:
            list_item_node.add_child_block(trans_block)

        while list_item.children:
            list_item_child = list_item.children.popleft()
            if not isinstance(list_item_child, TagElement):
                continue

            list_item_children_nodes = CONVERTERS[list_item_child.classification](
                list_item_node, list_item_child
            )
            list_item_node.add_child_nodes(list_item_children_nodes)

        list_item_nodes.append(list_item_node)

    return list_item_nodes


def convert_l_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    if tag.classification not in ["ul", "ol"]:
        raise ValueError(
            f"Unknown classification {tag.classification}, expected ul or ol"
        )

    block_type = LIST_TAG_CLASSIFICATION_TO_BLOCK_TYPE[tag.classification]

    list_items = deque()
    for child in tag.children:
        if child.classification == "li":
            list_items.append(child)

    return convert_list_item_to_node(parent, list_items, block_type)


def convert_list_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    if tag.classification not in ["ulist", "olist"]:
        raise ValueError(
            f"Unknown classification {tag.classification}, expected ulist or olist"
        )
    block_nodes = []

    elements = search_child_by_classification(tag, ["title", "ul", "ol"])
    title_element = None
    content_element = None

    for element in elements:
        if element.classification == "title":
            title_element = element
        if element.classification == "ul" or element.classification == "ol":
            content_element = element

    if title_element:
        title_block, _ = convert_text_with_trans_to_block(title_element, "toggle")

        title_node = BlockTree(parent, title_block)

        content_nodes = convert_l_to_node(title_node, content_element)
        title_node.add_child_nodes(content_nodes)

        block_nodes.append(title_node)
    else:
        block_nodes = convert_l_to_node(parent, content_element)

    return block_nodes


register(
    "paragraph",
    lambda parent, tag: convert_list_item_to_node(parent, deque([tag]), "paragraph"),
)

for classification in ["ol", "ul"]:
    register(classification, convert_l_to_node)

for classification in ["ulist", "olist"]:
    register(classification, convert_list_to_node)
