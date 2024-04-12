from typing import Optional

from pydantic import Field

from audit_logger.models.custom_base import CustomBaseModel


class BulkAuditLogOptions(CustomBaseModel):
    bulk_count: Optional[int] = Field(
        1,
        ge=1,
        le=500,
        description="Specifies the number of fake audit log entries to generate.",
        alias="bulk_limit",
    )
