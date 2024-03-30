from typing import Any, Dict, List, Optional

from pydantic import Field

from audit_logger.models.actor_details import ActorDetails
from audit_logger.models.custom_base import CustomBaseModel
from audit_logger.models.resource import ResourceDetails


class LogEntryDetails(CustomBaseModel):
    timestamp: Optional[str] = Field(
        default=None, description="The timestamp of the log entry."
    )
    event_name: Optional[str] = Field(
        default=None, description="The name of the event."
    )
    actor: Optional[ActorDetails] = Field(
        default=None, description="Details about the actor involved in the event."
    )
    action: Optional[str] = Field(default=None, description="The action performed.")
    comment: Optional[str] = Field(
        default=None, description="A comment regarding the log entry."
    )
    context: Optional[str] = Field(
        default=None, description="The context in which the event occurred."
    )
    resource: Optional["ResourceDetails"] = Field(
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
    server: Optional[Any] = Field(
        default=None,
        description="Information about the server related to the log entry.",
    )
    meta: Optional[Dict[str, Any]] = Field(
        default=None, description="Additional metadata associated with the log entry."
    )


class SearchResults(CustomBaseModel):
    hits: int = Field(default=0, description="The number of hits for the search query.")
    docs: List[Any] = Field(
        default=[], description="A list of documents that match the search query."
    )
    aggs: List[Any] = Field(
        default=[], description="A list of aggregations for the search query."
    )


class GenericResponse(CustomBaseModel):
    status: str = Field(default=None, description="The status of the response.")
    success_count: int = Field(
        default=None, description="The number of successful items in the response."
    )
    failed_count: int = Field(
        default=None, description="The number of failed items in the response."
    )
    failed_items: List[Dict] = Field(
        default=[], description="A list of items that failed."
    )
