from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from audit_logger.models.actor_details import ActorDetails
from audit_logger.models.resource import ResourceDetails
from audit_logger.models.server_details import ServerDetails


class AuditLogEntry(BaseModel):
    timestamp: Optional[str] = Field(
        default=None,
        description="The date and time when the event occurred, in ISO 8601 format.",
    )
    event_name: str = Field(description="Name of the event.")
    actor: Optional[ActorDetails] = Field(
        default=None,
        description="Details about the actor who initiated the event.",
    )
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
    meta: Dict[str, Any] = Field(
        default={}, description="Optional metadata about the event."
    )
