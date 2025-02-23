from __future__ import annotations

from enum import StrEnum


class Color(StrEnum):
    DEFAULT = "default"
    BLUE = "blue"
    BROWN = "brown"
    GRAY = "gray"
    GREEN = "green"
    ORANGE = "orange"
    PINK = "pink"
    PURPLE = "purple"
    RED = "red"
    YELLOW = "yellow"


class RichColor(Color):
    BLUE_BACKGROUND = "blue_background"
    BROWN_BACKGROUND = "brown_background"
    GRAY_BACKGROUND = "gray_background"
    GREEN_BACKGROUND = "green_background"
    ORANGE_BACKGROUND = "orange_background"
    PINK_BACKGROUND = "pink_background"
    PURPLE_BACKGROUND = "purple_background"
    RED_BACKGROUND = "red_background"
    YELLOW_BACKGROUND = "yellow_background"


class ParentType(StrEnum):
    DATABASE_ID = "database_id"
    PAGE_ID = "page_id"
    BLOCK_ID = "block_id"


class BlockType(StrEnum):
    BULLETED_LIST_ITEM = "bulleted_list_item"
    NUMBERED_LIST_ITEM = "numbered_list_item"
    PARAGRAPH = "paragraph"
    CALLOUT = "callout"
    DIVIDER = "divider"
    HEADER_1 = "header_1"
    HEADER_2 = "header_2"
    HEADER_3 = "header_3"
    TABLE = "table"
    TABLE_ROW = "table_row"
    IMAGE = "image"
    CODE = "code"

    @staticmethod
    def from_value(value: str) -> BlockType:
        return BlockType(value)


class PropertyType(StrEnum):
    TITLE = "title"
    SELECT = "select"
    URL = "url"
    MULTIPLE_SELECT = "multiple_select"


class LanguageType(StrEnum):
    JAVA = "java"
    DOCKER = "docker"
    KOTLIN = "kotlin"
    PYTHON = "python"
    XML = "xml"
    YAML = "yaml"
    SQL = "sql"
    JSON = "json"
    MARKDOWN = "markdown"
    PLAIN_TEXT = "plain_text"
    BASH = "bash"
    SHELL = "shell"
    POWERSHELL = "powershell"
    TYPESCRIPT = "typescript"
    JAVASCRIPT = "javascript"
