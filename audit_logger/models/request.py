from typing import Optional

from pydantic import BaseModel, Field


class RandomAuditLogSettings(BaseModel):
    fake_count: Optional[int] = Field(
        1,
        ge=1,
        le=350,
        description="Specifies the number of fake audit log entries to generate.",
    )
