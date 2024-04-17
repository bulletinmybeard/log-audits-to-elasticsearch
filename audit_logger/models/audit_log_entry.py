from datetime import datetime
from typing import Any, Dict, Optional, Union
from zoneinfo import ZoneInfo

from pydantic import Field, field_validator

from audit_logger.models.actor_details import ActorDetails
from audit_logger.models.custom_base import CustomBaseModel
from audit_logger.models.resource import ResourceDetails
from audit_logger.models.server_details import ServerDetails


def current_time(timezone: str = "Europe/Amsterdam") -> datetime:
    return datetime.now(ZoneInfo(timezone))


class AuditLogEntry(CustomBaseModel):
    timestamp: Optional[Union[datetime, str]] = Field(
        default_factory=current_time,
        description="The date and time when the event occurred, in ISO 8601 format.",
    )
    event_name: str = Field(description="Name of the event.")
    actor: ActorDetails = Field(
        default=None,
        description="Details about the actor who initiated the event.",
    )
    application_name: str = Field(description="Application name.")
    module: str = Field(description="Module name.")
    action: str = Field(description="Action performed.")
    comment: Optional[str] = Field(
        default=None, description="Optional comment about the event."
    )
    context: Optional[str] = Field(
        default=None,
        description="The operational context in which the event occurred.",
    )
    resource: Optional[ResourceDetails] = Field(
        default=None,
        description="Details about the resource.",
    )
    operation: Optional[str] = Field(
        default=None, description="Type of operation performed."
    )
    status: Optional[str] = Field(default=None, description="Status of the event.")
    endpoint: Optional[str] = Field(
        default=None,
        description="The API endpoint or URL accessed, if applicable.",
    )
    server: Optional[ServerDetails] = Field(
        default=None,
        description="Details about the server where the event occurred.",
    )
    meta: Optional[Dict[str, Any]] = Field(
        default={}, description="Optional metadata about the event."
    )

    @field_validator("timestamp")
    def format_timestamp(cls, v: Any) -> Union[datetime, str]:
        if isinstance(v, datetime):
            return v.isoformat()
        return v

    def to_hashable_tuple(self):
        # Create a hashable representation based on relevant log entry fields.
        return (self.timestamp, self.event_name, self.application_name, self.action)
