from typing import Any, Dict, List, Optional

from service_audit.models.resource import ResourceDetails
from service_audit.models.actor import ActorDetails

from pydantic import BaseModel, Field, IPvAnyAddress


class ServerInfo(BaseModel):
    hostname: Optional[str] = Field(
        default=None, description="The hostname of the server."
    )
    vm_name: Optional[str] = Field(
        default=None, description="The virtual machine name of the server."
    )
    ip_address: Optional[IPvAnyAddress] = Field(
        default=None, description="The IP address of the server."
    )


class LogEntryDetails(BaseModel):
    timestamp: Optional[str] = Field(
        default=None, description="The timestamp of the log entry."
    )
    event_name: Optional[str] = Field(
        default=None, description="The name of the event."
    )
    actor: Optional[ActorDetails] = Field(
        default=None, description="Details about the actor involved in the event."
    )
    action: Optional[str] = Field(
        default=None, description="The action performed."
    )
    comment: Optional[str] = Field(
        default=None, description="A comment regarding the log entry."
    )
    context: Optional[str] = Field(
        default=None, description="The context in which the event occurred."
    )
    resource: Optional['ResourceDetails'] = Field(
        default=None, description="Details about the resource involved in the event."
    )
    operation: Optional[str] = Field(
        default=None, description="The operation performed."
    )
    status: Optional[str] = Field(
        default=None, description="The status of the log entry."
    )
    endpoint: Optional[str] = Field(
        default=None, description="The endpoint associated with the log entry."
    )
    server_details: Optional[ServerInfo] = Field(
        default=None, description="Information about the server related to the log entry."
    )
    meta: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata associated with the log entry."
    )


class SearchResults(BaseModel):
    hits: int = Field(
        ..., description="The number of hits for the search query."
    )
    docs: List[Any] = Field(
        ..., description="A list of documents that match the search query."
    )
    aggs: List[Any] = Field(
        ..., description="A list of aggregations for the search query."
    )


class GenericResponse(BaseModel):
    status: str = Field(
        ..., description="The status of the response."
    )
    success_count: int = Field(
        ..., description="The number of successful items in the response."
    )
    failed_count: int = Field(
        ..., description="The number of failed items in the response."
    )
    failed_items: List[Dict] = Field(
        default=[], description="A list of items that failed."
    )
