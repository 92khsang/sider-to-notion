import importlib
import os
import pkgutil
from collections.abc import Callable
from typing import Dict, TYPE_CHECKING

if TYPE_CHECKING:
    from sider_to_notion.extractor import TagElement
    from sider_to_notion.sites import BlockTree

CONVERTERS: Dict[str, Callable[["BlockTree", "TagElement"], list["BlockTree"]]] = {}


def register(
    classification: str, fn: Callable[["BlockTree", "TagElement"], list["BlockTree"]]
) -> None:
    if classification in CONVERTERS:
        raise ValueError(f"Duplicate converter for tag '{classification}'")
    CONVERTERS[classification] = fn


def _load_converters():
    base_path = os.path.dirname(__file__)
    package = __name__.rsplit(".", 1)[0]
    for _, modname, _ in pkgutil.iter_modules([base_path]):
        if modname.startswith("_"):
            continue
        importlib.import_module(f"{package}.{modname}")


def collect_child_nodes(parent: "BlockTree", tag: "TagElement") -> list["BlockTree"]:
    child_nodes: list[BlockTree] = []

    while tag.children:
        child = tag.children.popleft()
        if hasattr(child, "tag_name"):
            child_nodes.extend(CONVERTERS[child.classification](parent, child))

    return child_nodes


for classification_ in ["preamble"]:
    register(classification_, collect_child_nodes)

_load_converters()
