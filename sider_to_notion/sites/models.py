import weakref
from collections import deque
from enum import Enum
from typing import TYPE_CHECKING, Optional

from pydantic import BaseModel, ConfigDict

if TYPE_CHECKING:
    from pynotion.models import TxBlock


class DocType(str, Enum):
    SPRING = "spring"


class Doc(BaseModel):
    model_config = ConfigDict(frozen=True)

    url: str
    type: DocType
    html_str: Optional[str] = None


class BlockTree:
    __slots__ = ("_parent_ref", "children", "tx_block", "__weakref__")

    if TYPE_CHECKING:
        children: deque["BlockTree"]
        tx_block: Optional["TxBlock"]

    def __init__(
        self,
        parent: Optional["BlockTree"] = None,
        tx_block: Optional["TxBlock"] = None,
    ):
        if parent and not isinstance(parent, BlockTree):
            raise TypeError(f"parent must be BlockTree, not {type(parent)}")
        if isinstance(tx_block, BlockTree):
            raise TypeError(f"tx_block must be TxBlock, not {type(tx_block)}")

        self._parent_ref = weakref.ref(parent) if parent else None
        self.children: deque["BlockTree"] = deque()
        self.tx_block = tx_block

    @property
    def parent(self) -> Optional["BlockTree"]:
        return self._parent_ref() if self._parent_ref else None

    def add_child_node(self, child: "BlockTree"):
        self.children.append(child)

    def add_child_nodes(self, children: list["BlockTree"]):
        self.children.extend(children)

    def add_child_block(self, child_block: "TxBlock"):
        self.children.append(BlockTree(self, child_block))
