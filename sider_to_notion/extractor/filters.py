from typing import Literal, Optional

from pydantic import BaseModel

__all__ = ["DivFilter"]


class DivFilter(BaseModel):
    value: str
    type: Literal["id", "class"] = "class"
    classification: Optional[str] = None
