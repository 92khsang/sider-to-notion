from __future__ import annotations as _annotations

from collections import deque
from typing import TYPE_CHECKING, Collection

from pynotion.models import (
    TxTableRowBlock,
    TxTableRow,
    TxCallout,
    TxCalloutBlock,
    TxTableBlock,
    TxTable,
    SingleEmoji,
)

from sider_to_notion.extractor import TagElement
from sider_to_notion.sites.models import BlockTree
from ._registry import register, CONVERTERS
from ._utils import (
    search_child_by_classification,
    create_tx_rich_text,
)
from .text import convert_text_with_trans_to_block

if TYPE_CHECKING:
    from pynotion.models import TxRichText


def _check_length(target: Collection, expected_length: int):
    if len(target) != expected_length:
        raise ValueError(f"Expected {expected_length} elements, but got {len(target)}")


def _extract_row_elements(tag: TagElement) -> deque[TagElement]:
    tbody_element = search_child_by_classification(tag, "tbody")
    _check_length(tbody_element, 1)

    return search_child_by_classification(tbody_element[0], "tr")


def _create_row_blocks(
    row_elements: deque[TagElement], element_type: str
) -> list[TxTableRowBlock]:
    """
    Generalized function to create table row blocks.

    Args:
        row_elements: deque of row elements to process
        element_type: type of cell element ('td' or 'th')

    Returns:
        list of created TxTableRowBlock objects
    """
    row_blocks: list[TxTableRowBlock] = []

    while row_elements:
        row_element = row_elements.popleft()
        cell_elements = search_child_by_classification(row_element, element_type)

        cells: list[list[TxRichText]] = []
        while cell_elements:
            cell_element = cell_elements.popleft()

            # Apply different processing based on an element type
            if element_type == "th":
                cell_block, _ = convert_text_with_trans_to_block(
                    cell_element, "paragraph"
                )
                rich_texts: list[TxRichText] = cell_block.paragraph.rich_text
            else:  # element_type == "td"
                p_tags = search_child_by_classification(cell_element, "p")
                if len(p_tags) == 0:
                    cell_block = create_tx_rich_text("")
                    rich_texts: list[TxRichText] = [cell_block]
                else:
                    _check_length(p_tags, 1)
                    cell_block, _ = convert_text_with_trans_to_block(
                        p_tags[0], "paragraph"
                    )
                    rich_texts: list[TxRichText] = cell_block.paragraph.rich_text

            cells.append(rich_texts)

        row_block = TxTableRowBlock(table_row=TxTableRow(cells=cells))
        row_blocks.append(row_block)

    return row_blocks


def convert_table_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    if "tableblock" not in tag.classes:
        raise ValueError(
            f"Expected a table with class 'tableblock' in a table block, but got {tag.classes}"
        )

    table_row_blocks: list[TxTableRowBlock] = []

    table_elements = search_child_by_classification(tag, ["thead", "tbody"])
    table_element: TagElement = table_elements.popleft()
    has_header = table_element.tag_name == "thead"

    if has_header:
        thead_row_elements = search_child_by_classification(table_element, "tr")
        _check_length(thead_row_elements, 1)
        table_row_blocks.extend(_create_row_blocks(thead_row_elements, "th"))

        table_element = table_elements.popleft()

    if table_element.tag_name != "tbody":
        raise ValueError(
            f"Expected a table with class 'tableblock' in a table block, but got {tag.classes}"
        )

    row_elements = search_child_by_classification(table_element, "tr")
    table_row_blocks.extend(_create_row_blocks(row_elements, "td"))

    table_block = TxTableBlock(
        table=TxTable(
            table_width=len(table_row_blocks[0].table_row.cells),
            has_column_header=has_header,
            has_row_header=False,
            children=table_row_blocks,
        )
    )

    table_node = BlockTree(parent, table_block)
    return [table_node]


def convert_colist_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    table_element = search_child_by_classification(tag, "table")
    _check_length(table_element, 1)

    colist_nodes: list[BlockTree] = []
    row_elements = _extract_row_elements(table_element[0])
    while row_elements:
        row_element = row_elements.popleft()
        cell_elements = search_child_by_classification(row_element, "td")
        _check_length(cell_elements, 2)

        content_element = cell_elements[1]
        content_block, trans_block = convert_text_with_trans_to_block(
            content_element, "numbered_list_item"
        )
        content_node = BlockTree(parent, content_block)
        if trans_block:
            content_node.add_child_block(trans_block)

        colist_nodes.append(content_node)

    return colist_nodes


def convert_note_to_node(parent: BlockTree, tag: TagElement) -> list[BlockTree]:
    table_element = search_child_by_classification(tag, "table")
    _check_length(table_element, 1)

    row_elements = _extract_row_elements(table_element[0])
    _check_length(row_elements, 1)

    td_elements = search_child_by_classification(row_elements[0], "td")
    _check_length(td_elements, 2)

    note_type_elements = search_child_by_classification(td_elements.popleft(), "i")
    _check_length(note_type_elements, 1)

    note_type_element = note_type_elements[0]
    callout_block = TxCalloutBlock(
        callout=TxCallout(
            rich_text=[create_tx_rich_text(note_type_element.attrs.get("title"))],
            icon=SingleEmoji(emoji="💡"),
        )
    )

    callout_node = BlockTree(parent, callout_block)

    td_element: TagElement = td_elements.popleft()
    if not any(child.classification == "paragraph" for child in td_element.children):
        p_block, trans_block = convert_text_with_trans_to_block(td_element, "paragraph")

        cell_node = BlockTree(parent, p_block)
        if trans_block:
            cell_node.add_child_block(trans_block)

        callout_node.add_child_node(cell_node)

    while td_element.children:
        cell_element = td_element.children.popleft()
        if not isinstance(cell_element, TagElement):
            continue

        if cell_element.classification == "title":
            cell_element.classification = "p"

        cell_nodes = CONVERTERS[cell_element.classification](parent, cell_element)
        callout_node.add_child_nodes(cell_nodes)

    return [callout_node]


register("table", convert_table_to_node)
register("colist", convert_colist_to_node)
register("admonitionblock", convert_note_to_node)
