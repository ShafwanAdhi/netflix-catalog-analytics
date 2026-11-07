"""Duration input contract for this task."""
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field


class Duration(BaseModel):
    model_config = ConfigDict(extra="forbid")
    value: int = Field(gt=0, strict=True)
    unit: Literal["minutes", "seasons"]


