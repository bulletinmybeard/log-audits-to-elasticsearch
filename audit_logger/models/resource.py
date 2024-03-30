from typing import Optional

from pydantic import Field

from audit_logger.models.custom_base import CustomBaseModel


class ResourceDetails(CustomBaseModel):
    type: Optional[str] = Field(
        default=None,
        description="Type of the resource that was acted upon.",
    )
    id: Optional[str] = Field(
        default=None,
        description="Unique identifier of the resource.",
    )
