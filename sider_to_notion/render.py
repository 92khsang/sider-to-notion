import logging
from dataclasses import dataclass
from typing import TYPE_CHECKING, Self, Any, Optional
from uuid import UUID

from pynotion import PyNotion
from tqdm import tqdm

if TYPE_CHECKING:
    from sider_to_notion.sites import BlockTree
    from pynotion.models import RxPage, TxPropertyValue


@dataclass(frozen=True)
class NotionDocPageInfo:
    parent_id: UUID
    title: str
    link: str
    version: Optional[str] = None
    tag: Optional[list[str]] = None


class NotionRenderer:
    def __init__(self, token: str):
        self._token = token
        self._pynotion: PyNotion = PyNotion(token=self._token, async_mode=False)
        self._progress_bar = None

    def start_progress(self, tree: "BlockTree"):
        total = self._count_total_blocks(tree)
        self._progress_bar = tqdm(total=total, desc="Rendering to Notion")

    def _count_total_blocks(self, tree: "BlockTree") -> int:
        return 1 + sum(self._count_total_blocks(child) for child in tree.children)

    def render_page(self, page_info: NotionDocPageInfo) -> "RxPage":
        from pynotion.models import (
            DatabaseParent,
            Text,
            TxOptionValue,
            TxPage,
            TxTextRichText,
            TxTitlePropertyValue,
            TxUrlPropertyValue,
        )

        properties: dict[str, "TxPropertyValue"] = {
            "Name": TxTitlePropertyValue(
                title=[TxTextRichText(text=Text(content=page_info.title))]
            ),
            "Link": TxUrlPropertyValue(url=page_info.link),
        }

        if page_info.version:
            from pynotion.models import TxSelectPropertyValue

            properties["Version"] = TxSelectPropertyValue(
                select=TxOptionValue(name=page_info.version)
            )

        if page_info.tag:
            from pynotion.models import TxMultiSelectPropertyValue

            properties["Tag"] = TxMultiSelectPropertyValue(
                multi_select=[TxOptionValue(name=tag) for tag in page_info.tag]
            )

        tx_page = TxPage(
            parent=DatabaseParent(database_id=page_info.parent_id),
            properties=properties,
        )

        return self._pynotion.pages.create_page(tx_page)

    def render_blocks(self, parent_id: UUID, tree: "BlockTree"):
        if not tree.children:
            if self._progress_bar:
                self._progress_bar.update(1)
            return

        try:
            blocks = self._pynotion.blocks.append_block_children(
                parent_id=parent_id,
                children=[b.tx_block for b in tree.children],
            )
        except Exception as e:
            logging.error(
                f"Failed to append blocks: parent_id={parent_id}, block: {tree.tx_block.model_dump(mode='json', exclude_none=True)}, error: {e}"
            )
            raise

        if len(tree.children) != len(blocks.results):
            raise ValueError(
                f"Expected {len(tree.children)} blocks, but got {len(blocks.results)}"
            )

        if self._progress_bar:
            self._progress_bar.update(1)

        for idx, rx_block in enumerate(blocks.results):
            self.render_blocks(rx_block.id, tree.children[idx])

    def __del__(self):
        if self._pynotion:
            self._pynotion.close()
        if self._progress_bar:
            self._progress_bar.close()

    def __enter__(self) -> Self:
        return self

    def __exit__(self, exc_type: Any, exc_val: Any, exc_tb: Any):
        self._pynotion.close()
        if self._progress_bar:
            self._progress_bar.close()
