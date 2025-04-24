from typing import Annotated

from pydantic import BaseModel, Field


class ExcludeTag(BaseModel):
    tag: str
    attrs: Annotated[dict[str, set[str]], Field(default_factory=dict)]


class ExcludeTags(BaseModel):
    tags: Annotated[list[ExcludeTag], Field(default_factory=list)]
