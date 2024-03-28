from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from audit_logger.models.actor_details import ActorDetails
from audit_logger.models.resource import ResourceDetails
from audit_logger.models.server_details import ServerDetails


class AuditLogEntry(BaseModel):
    timestamp: str = Field(
        default=None,
        title="Timestamp",
        description="The date and time when the event occurred, in ISO 8601 format.",
    )
    event_name: str = Field(title="Event Name", description="Name of the event.")
    actor: ActorDetails = Field(
        default=None,
        title="Actor",
        description="Details about the actor who initiated the event.",
    )
    action: str = Field(title="Action", description="Action performed.")
    comment: Optional[str] = Field(
        default=None, title="Comment", description="Optional comment about the event."
    )
    context: str = Field(
        default=None,
        title="Context",
        description="The operational context in which the event occurred.",
    )
    resource: ResourceDetails = Field(
        default=None,
        title="Resource",
        description="Details about the resource.",
    )
    operation: str = Field(
        default=None, title="Operation", description="Type of operation performed."
    )
    status: str = Field(
        default=None, title="Status", description="Status of the event."
    )
    endpoint: Optional[str] = Field(
        default=None,
        title="Endpoint",
        description="The API endpoint or URL accessed, if applicable.",
    )
    server: ServerDetails = Field(
        default=None,
        title="Server Details",
        description="Details about the server where the event occurred.",
    )
    meta: Optional[Dict[str, Any]] = Field(
        default={}, title="Meta", description="Optional metadata about the event."
    )
