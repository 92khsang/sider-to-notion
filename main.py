import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import TYPE_CHECKING
from uuid import UUID

from dotenv import load_dotenv

from sider_to_notion import (
    NotionRenderer,
    NotionDocPageInfo,
    DocType,
    document_registry,
)
from sider_to_notion.debug import print_element_tree

if TYPE_CHECKING:
    from sider_to_notion.sites import BlockTree

load_dotenv()

PROJECT_ROOT = Path(os.getenv("PROJECT_ROOT", Path.cwd())).resolve()
DEFAULT_ASSETS_DIR = Path(os.getenv("ASSETS_DIR", PROJECT_ROOT / "assets")).resolve()


@dataclass
class ProcessConfig:
    doc_type: DocType
    base_url: str
    html_file: Path
    assets_dir: Path
    debug: bool = False

    @property
    def html_output_path(self) -> Path:
        html_name = self.base_url.split("/")[-1]
        return self.assets_dir / f"{html_name.split('.')[0]}_debug.html"


@dataclass
class RenderConfig:
    notion_token: str
    database_id: UUID
    title: str
    version: str
    link: str
    tags: list[str] = field(default_factory=list)


def parse_config() -> tuple[ProcessConfig, RenderConfig]:
    parser = argparse.ArgumentParser(
        description="Convert HTML documentation into Notion format."
    )

    parser.add_argument("--doc-type", type=str, default=os.getenv("DOC_TYPE"))
    parser.add_argument("--notion-token", type=str, default=os.getenv("NOTION_TOKEN"))
    parser.add_argument("--database-id", type=str, default=os.getenv("DATABASE_ID"))
    parser.add_argument("--base-url", type=str, default=os.getenv("BASE_URL"))
    parser.add_argument("--html-file", type=str, default=os.getenv("HTML_FILE"))
    parser.add_argument("--title", type=str, default=os.getenv("TITLE"))
    parser.add_argument("--version", type=str, default=os.getenv("VERSION"))
    parser.add_argument("--assets-dir", type=str, default=str(DEFAULT_ASSETS_DIR))
    parser.add_argument("--debug", action="store_true")

    args = parser.parse_args()

    missing = [
        name
        for name in [
            "notion_token",
            "database_id",
            "base_url",
            "html_file",
            "title",
            "version",
        ]
        if not getattr(args, name)
    ]
    if missing:
        parser.error(
            f"Missing required arguments or .env variables: {', '.join(missing)}"
        )

    process_config = ProcessConfig(
        doc_type=DocType(args.doc_type),
        base_url=args.base_url,
        html_file=Path(args.html_file),
        assets_dir=Path(args.assets_dir).resolve(),
        debug=args.debug,
    )

    render_config = RenderConfig(
        notion_token=args.notion_token,
        database_id=UUID(args.database_id),
        title=args.title,
        version=args.version,
        link=args.base_url,
    )

    return process_config, render_config


def process(config: ProcessConfig) -> "BlockTree":
    config.assets_dir.mkdir(parents=True, exist_ok=True)

    processor = document_registry.fetch(config.doc_type)

    html_text = (config.assets_dir / config.html_file).read_text(encoding="utf-8")
    soup = processor.read(config.base_url, html_text)
    elements = processor.extract(soup)

    if config.debug:
        config.html_output_path.write_text(soup.prettify(), encoding="utf-8")
        print_element_tree(elements)

    block_tree = processor.assemble(elements)
    return block_tree


def render_to_notion(config: RenderConfig, block_tree: "BlockTree"):
    page_info = NotionDocPageInfo(
        parent_id=config.database_id,
        title=config.title,
        version=config.version,
        tag=config.tags,
        link=config.link,
    )

    with NotionRenderer(config.notion_token) as render:
        render.start_progress(block_tree)
        page = render.render_page(page_info)
        render.render_blocks(page.id, block_tree)


def main():
    process_config, render_config = parse_config()
    block_tree = process(process_config)
    render_to_notion(render_config, block_tree)


if __name__ == "__main__":
    main()
