from typing import Optional

from pydantic import BaseModel, Extra, Field


class RandomAuditLogSettings(BaseModel):
    bulk_count: Optional[int] = Field(
        1,
        ge=1,
        le=350,
        description="Specifies the number of fake audit log entries to generate.",
    )

    # Forbid extra fields and raise an exception if any are found.
    class Config:
        extra = Extra.forbid
