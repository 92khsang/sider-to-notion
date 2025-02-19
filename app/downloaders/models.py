from __future__ import annotations

from collections import defaultdict
from dataclasses import field, dataclass
from typing import TYPE_CHECKING, NamedTuple

if TYPE_CHECKING:
    TAG_NAME: str
    ATTR_NAME: str
    ATTR_VALUE: str


class ExcludeTag(NamedTuple):
    tag: str
    attrs: dict[str, set[str]] = defaultdict(set)


@dataclass(frozen=True, slots=True)
class ExcludeTags:
    tags: list[ExcludeTag] = field(default_factory=list)

    @classmethod
    def from_list(
        cls, excludes: list[tuple[TAG_NAME, dict[ATTR_NAME, ATTR_VALUE]]]
    ) -> ExcludeTags:
        tags = []
        for exclude in excludes:
            tag, attrs = exclude
            attrs = {key: set(value.split(",")) for key, value in attrs.items()}
            tags.append(ExcludeTag(tag, attrs))
        return cls(tags)
