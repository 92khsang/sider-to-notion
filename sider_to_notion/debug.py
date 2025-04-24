import json
from typing import TYPE_CHECKING

from sider_to_notion.extractor import TagElement, NavStringElement

if TYPE_CHECKING:
    from sider_to_notion.extractor import Element
    from sider_to_notion.sites import BlockTree


def print_element_tree(node: "Element", indent: int = 0) -> None:
    prefix = "  " * indent
    level_info = f"[level={indent}]"

    if isinstance(node, TagElement):
        attrs = json.dumps(node.attrs, ensure_ascii=False) if node.attrs else "{}"
        print(f"{prefix}- {level_info} <{node.tag_name}:{node.classification}> {attrs}")
    elif isinstance(node, NavStringElement):
        print(f'{prefix}- {level_info} "{node.text(True)}"')
    else:
        print(f"{prefix}- {level_info} Unknown node type")

    for child in node.children:
        print_element_tree(child, indent + 1)


def print_block_tree(t: "BlockTree", indent: int = 0):
    prefix = "  " * indent
    level_info = f"[level={indent}]"

    if t.tx_block:
        block_json = t.tx_block.model_dump(
            mode="json", exclude_none=True, exclude_unset=True, exclude_defaults=True
        )
        json_str = json.dumps(block_json, ensure_ascii=False, indent=2)
        lines = json_str.splitlines()

        print(f"{prefix}- {level_info} {lines[0]}")
        for line in lines[1:]:
            print(f"{prefix}  {line}")
    else:
        print(f"{prefix}- {level_info} (empty)")

    for child in t.children:
        print_block_tree(child, indent + 1)
