# Sider to Notion

A CLI tool to convert HTML documentation (e.g., Spring Docs) into structured Notion pages using the [Notion API](https://developers.notion.com/).

## Features

- HTML parsing and cleanup using BeautifulSoup
- Structured block tree generation from tag elements
- Modular extractors and Notion block assemblers
- Supports sectioning, tables, images, lists, and translation toggles
- CLI interface with `argparse` and `.env` support
- Progress bar using `tqdm`

## Requirements

- Python 3.10 – 3.13
- Poetry (recommended)
- Notion integration token

## Installation

```bash
poetry install
```

## Configuration

Create a `.env` file or pass values via CLI flags:

```env
DOC_TYPE=spring
NOTION_TOKEN=your_secret_token
DATABASE_ID=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
BASE_URL=https://docs.spring.io/spring-framework/reference/web/webflux.html
HTML_FILE=./assets/webflux.html
TITLE=Spring WebFlux
VERSION=6.1.2
```

## Usage

```bash
poetry run python main.py
```

Or with CLI arguments:

```bash
poetry run python main.py \
  --doc-type spring \
  --notion-token YOUR_TOKEN \
  --database-id YOUR_DATABASE_ID \
  --base-url https://docs.spring.io/spring-framework/reference/web/webflux.html \
  --html-file ./assets/webflux.html \
  --title "Spring WebFlux" \
  --version 6.1.2
```

Enable debug mode to inspect the element tree:

```bash
poetry run python main.py --debug
```

## Project Structure

- `fetcher/`: Downloads and filters raw HTML
- `extractor/`: Converts HTML tags into structured element trees
- `sites/`: Site-specific extraction/assembly logic (e.g., Spring)
- `render.py`: Renders Notion blocks and pages using `pynotion`
- `main.py`: CLI entry point

## License

MIT
