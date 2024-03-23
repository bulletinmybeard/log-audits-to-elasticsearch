import logging
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator, model_validator

logger = logging.getLogger("service_audit")

available_fields = {
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


class SearchParams(BaseModel):
    """Performs search queries on the Elasticsearch audit log index."""

    max_results: Optional[int] = Field(
        500, ge=1, le=1000, description="Limit the number of hits returned."
    )
    include_fields: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Specific fields to include in the search results.",
    )
    exclude_fields: Optional[Union[List[str], str]] = Field(
        default=None,
        description="Specific fields to exclude in the search results.",
    )
    sort_by: Optional[str] = Field(default="timestamp", description="Field to sort by")
    sort_order: Optional[str] = Field(
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
    aggregations: Optional[Any] = Field(
        None, description="Aggregation queries to run alongside the search."
    )

    @field_validator("sort_order")
    def sort_order_valid(cls, v: str) -> str:
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v

    @model_validator(mode="after")
    def validate_multiple_attributes(cls, v) -> Any:
        # Conditional validation for including or excluding ES document fields.
        if v.exclude_fields is not None and v.include_fields is not None:
            raise ValueError(
                "Cannot specify both 'include_fields' "
                "and 'exclude_fields'. Choose either one of them."
            )
        elif v.exclude_fields is None and (
            v.include_fields is not None and len(v.include_fields) == 0
        ):
            raise ValueError("'include_fields' does not contain fields to include.")
        elif v.include_fields is None and (
            v.exclude_fields is not None and len(v.exclude_fields) == 0
        ):
            raise ValueError("'exclude_fields' does not contain fields to include.")

        return v
