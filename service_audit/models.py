from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class ActorModel(BaseModel):
    identifier: str = Field(
        ..., title="Identifier", description="Unique identifier of the actor."
    )
    type: str = Field(
        ..., title="Type", description="Type of actor, e.g., 'user' or 'system'."
    )
    ip_address: str = Field(
        ..., title="IP Address", description="IP address of the actor."
    )
    user_agent: str = Field(
        ..., title="User Agent", description="User agent string of the actor's device."
    )


class ResourceModel(BaseModel):
    type: str = Field(
        ...,
        title="Resource Type",
        description="Type of the resource that was acted upon.",
    )
    id: str = Field(
        ..., title="Resource ID", description="Unique identifier of the resource."
    )


class ServerDetailsModel(BaseModel):
    hostname: str = Field(
        ...,
        title="Hostname",
        description="Hostname of the server where the event occurred.",
    )
    vm_name: str = Field(
        ...,
        title="VM Name",
        description="Name of the virtual machine where the event occurred.",
    )
    ip_address: str = Field(
        ..., title="IP Address", description="IP address of the server."
    )


class AuditLogEntry(BaseModel):
    timestamp: str = Field(
        ...,
        title="Timestamp",
        description="The date and time when the event occurred, in ISO 8601 format.",
    )
    event_name: str = Field(..., title="Event Name", description="Name of the event.")
    actor: ActorModel = Field(
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
    resource: ResourceModel = Field(
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
    server_details: ServerDetailsModel = Field(
        ...,
        title="Server Details",
        description="Details about the server where the event occurred.",
    )
    meta: Dict[str, Any] = Field(
        {}, title="Meta", description="Optional metadata about the event."
    )


class SearchParams(BaseModel):
    max_results: int = Field(
        500, ge=1, le=500, description="Limit the number of hits returned."
    )
    fields: Union[List[str], str] = Field(
        default="all",
        description="Specific fields to include in the search results or 'all' for everything.",
    )
    sort_by: str = Field(default="timestamp", description="Field to sort by")
    sort_order: str = Field(
        default="asc",
        description="Sort order: 'asc' for ascending or 'desc' for descending.",
    )
    date_range_start: Optional[str] = Field(
        None, description="Start of the date range for filtering (inclusive)."
    )
    date_range_end: Optional[str] = Field(
        None, description="End of the date range for filtering (inclusive)."
    )
    search_query: Optional[str] = Field(
        None, description="A text search query to match."
    )
    exact_matches: Optional[Dict[str, Union[str, List[str]]]] = Field(
        None, description="Fields with specific values to match exactly."
    )
    include_nested: Optional[bool] = Field(
        False, description="Whether to include nested fields in the search."
    )
    text_search_fields: Optional[Dict[str, str]] = Field(
        None, description="Free text search queries mapped to specific fields."
    )
    exclusions: Optional[Dict[str, Union[str, List[str]]]] = Field(
        None,
        description="Fields with specific values to be excluded from the search results.",
    )
    min_should_match: Optional[int] = Field(
        None, description="Minimum number of 'should' clauses that must match."
    )
    aggregations: Optional[Dict[str, Dict]] = Field(
        None, description="Aggregation queries to run alongside the search."
    )

    @field_validator("fields")
    def validate_fields(cls, value):
        allowed_fields = {
            "timestamp",
            "event_name",
            "actor.identifier",
            "actor.type",
            "actor.ip_address",
            "actor.user_agent",
            "action",
            "comment",
            "context",
            "resource.type",
            "resource.id",
            "operation",
            "status",
            "endpoint",
            "server_details.hostname",
            "server_details.vm_name",
            "server_details.ip_address",
        }
        if value == "all":
            return list(allowed_fields)
        if isinstance(value, list):
            if not all(item in allowed_fields for item in value):
                raise ValueError(f"Fields must consist of {allowed_fields}")
            return value
        raise ValueError("fields must be either 'all' or a list of allowed field names")

    @field_validator("sort_order")
    def sort_order_valid(cls, value):
        if value not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return value
