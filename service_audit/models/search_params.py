from typing import Dict, List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class SearchParams(BaseModel):
    max_results: Optional[int] = Field(
        500, ge=1, le=1000, description="Limit the number of hits returned."
    )
    fields: Optional[Union[List[str], str]] = Field(
        default="all",
        description="Specific fields to include in the search results or 'all' for everything.",
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
    min_should_match: Optional[int] = Field(
        None, description="Minimum number of 'should' clauses that must match."
    )
    aggregations: Optional[Dict[str, Dict]] = Field(
        None, description="Aggregation queries to run alongside the search."
    )

    @field_validator("fields")
    def validate_fields(cls, value: Union[List[str], str]) -> Union[List[str], str]:
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
    def sort_order_valid(cls, value: str) -> str:
        if value not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return value
