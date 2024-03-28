from typing import Optional

from pydantic import BaseModel, Field


class ResourceDetails(BaseModel):
    type: Optional[str] = Field(
        default=None,
        description="Type of the resource that was acted upon.",
    )
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the resource.",
    )
