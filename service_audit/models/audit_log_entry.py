from typing import Any, Dict, Optional

from pydantic import BaseModel, Field

from service_audit.models.actor import ActorDetails
from service_audit.models.resource import ResourceDetails
from service_audit.models.server_details import ServerInfo


class AuditLogEntry(BaseModel):
    timestamp: str = Field(
        ...,
        title="Timestamp",
        description="The date and time when the event occurred, in ISO 8601 format.",
    )
    event_name: str = Field(..., title="Event Name", description="Name of the event.")
    actor: ActorDetails = Field(
        ...,
        title="Actor",
        description="Details about the actor who initiated the event.",
    )
    action: str = Field(..., title="Action", description="Action performed.")
    comment: Optional[str] = Field(
        None, title="Comment", description="Optional comment about the event."
    )
    context: str = Field(
        ...,
        title="Context",
        description="The operational context in which the event occurred.",
    )
    resource: ResourceDetails = Field(
        ...,
        title="Resource",
        description="Details about the resource.",
    )
    operation: str = Field(
        ..., title="Operation", description="Type of operation performed."
    )
    status: str = Field(..., title="Status", description="Status of the event.")
    endpoint: Optional[str] = Field(
        None,
        title="Endpoint",
        description="The API endpoint or URL accessed, if applicable.",
    )
    server_details: ServerInfo = Field(
        ...,
        title="Server Details",
        description="Details about the server where the event occurred.",
    )
    meta: Dict[str, Any] = Field(
        {}, title="Meta", description="Optional metadata about the event."
    )
