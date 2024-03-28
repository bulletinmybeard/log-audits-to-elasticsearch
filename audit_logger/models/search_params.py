import logging
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Extra, Field, field_validator, model_validator

from audit_logger.utils import is_valid_ip_v4_address, validate_date

logger = logging.getLogger("audit_logger")


class MaxResultsMixin(BaseModel):
    max_results: Optional[int] = Field(
        500,
        ge=1,
        le=1000,
        description="Specifies the max number of hits to return, between 1 and 1000 inclusive.",
    )


class SortOrderEnum(str, Enum):
    ASC = "asc"
    DESC = "desc"


class FieldSelectionMode(str, Enum):
    INCLUDE = "include"
    EXCLUDE = "exclude"


class FilterTypeEnum(str, Enum):
    EXACT = "exact"
    TEXT_SEARCH = "text_search"
    RANGE = "range"
    WILDCARD = "wildcard"
    EXISTS = "exists"
    MISSING = "missing"
    NESTED = "nested"


class FieldIdentifierEnum(str, Enum):
    TIMESTAMP = "timestamp"
    EVENT_NAME = "event_name"
    ACTOR = "actor"
    ACTOR_IDENTIFIER = "actor.identifier"
    ACTOR_TYPE = "actor.type"
    ACTOR_IP_ADDRESS = "actor.ip_address"
    ACTOR_USER_AGENT = "actor.user_agent"
    ACTION = "action"
    COMMENT = "comment"
    CONTEXT = "context"
    RESOURCE = "resource"
    RESOURCE_TYPE = "resource.type"
    RESOURCE_ID = "resource.id"
    OPERATION = "operation"
    STATUS = "status"
    ENDPOINT = "endpoint"
    SERVER = "server"
    SERVER_HOSTNAME = "server.hostname"
    SERVER_VM_NAME = "server.vm_name"
    SERVER_IP_ADDRESS = "server.ip_address"


class AggregationTypeEnum(str, Enum):
    TERMS = "terms"
    VALUE_COUNT = "value_count"
    AVG = "avg"
    NESTED = "nested"
    DATE_HISTOGRAM = "date_histogram"


class SearchFilterParams(BaseModel):
    field: FieldIdentifierEnum = Field(
        default=None,
        description="",
    )
    type: FilterTypeEnum = Field(
        default=None,
        description="",
    )
    value: Optional[Union[str, int, float, Decimal]] = Field(
        default=None,
        description="",
    )
    values: Optional[List[Union[str, int, float, Decimal]]] = Field(
        default=None,
        description="",
    )
    gte: Optional[Union[str, int, float, Decimal]] = Field(
        default=None,
        description="",
    )
    lte: Optional[Union[str, int, float, Decimal]] = Field(
        default=None,
        description="",
    )

    @model_validator(mode="after")
    def validate_filter_fields(cls, v):
        if v.type == FilterTypeEnum.RANGE:
            # Check if the field is a date and validate the 'gte' and 'lte' values.
            if v.field == FieldIdentifierEnum.TIMESTAMP:
                if not all((validate_date(v.gte), validate_date(v.lte))):
                    raise ValueError(
                        f"For a date 'range' filter, 'gte' and 'lte' must be valid dates (YYYY-MM-DDTHH:MM:SSZ)."  # noqa
                    )
            # Check if the field is an IP address and validate the 'gte' and 'lte' values.
            if v.field in [
                FieldIdentifierEnum.ACTOR_IP_ADDRESS,
                FieldIdentifierEnum.SERVER_IP_ADDRESS,
            ]:
                if not all(
                    (is_valid_ip_v4_address(v.gte), is_valid_ip_v4_address(v.lte))
                ):
                    raise ValueError(
                        f"For an IP address range filter, 'gte' and 'lte' must be valid IPv4 addresses."  # noqa
                    )
        elif v.type == FilterTypeEnum.MISSING:
            pass

        # TODO: Add more checks for other types as needed!!!
        return v

    @field_validator("field")
    def check_field_is_valid(cls, v):
        if v not in FieldIdentifierEnum:
            raise ValueError(f"field must be one of {list(FieldIdentifierEnum)}")
        return v

    @field_validator("type")
    def check_type_is_valid(cls, v):
        if v not in FilterTypeEnum:
            raise ValueError(f"type must be one of {list(FilterTypeEnum)}")
        return v


class AggregationFilterParams(BaseModel):
    range: Optional[Dict[str, Dict[str, str]]]


class SubAggregationConfig(BaseModel):
    type: AggregationTypeEnum
    field: FieldIdentifierEnum


class AggregationSetup(MaxResultsMixin, BaseModel):
    type: AggregationTypeEnum = Field(
        ..., description="Specifies the type of aggregation."
    )
    field: FieldIdentifierEnum = Field(..., description="The field to aggregate on.")
    sub_aggregations: Optional[List[SubAggregationConfig]] = Field(
        default=None, description="List of sub-aggregations to apply."
    )
    interval: Optional[str] = Field(
        default=None,
        description="Interval for date histogram aggregations, if applicable.",
    )
    filter: Optional[AggregationFilterParams] = Field(
        default=None, description="Filter to apply to the aggregation."
    )


class SearchParamsV2(MaxResultsMixin, BaseModel):
    fields: Optional[List[FieldIdentifierEnum]] = Field(
        default=None,
        description="Fields to include in results. Empty includes all fields.",
    )
    fields_mode: Optional[FieldSelectionMode] = Field(
        default=FieldSelectionMode.INCLUDE,
        description="Determines if `fields` are included or excluded. INCLUDE or EXCLUDE.",
    )
    sort_by: Optional[FieldIdentifierEnum] = Field(
        default="timestamp", description="Field to sort the search results by."
    )
    sort_order: Optional[SortOrderEnum] = Field(
        default="asc",
        description="Sort order of results: 'asc' for ascending, 'desc' for descending.",
    )
    filters: Optional[List[SearchFilterParams]] = Field(
        default=None,
        description="Filters to apply for refined search results.",
    )
    aggs: Optional[Union[List[AggregationSetup], Dict[str, Any]]] = Field(
        default=None,
        description="Aggregations to apply for data summarization/analysis.",
    )

    # Forbid extra fields and raise an exception if any are found.
    class Config:
        extra = Extra.forbid

    @field_validator("sort_order")
    def sort_order_valid(cls, v: str) -> str:
        if v not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v


# DEPRECATED !!!!!!!!!!!!!!
# DEPRECATED !!!!!!!!!!!!!!
# DEPRECATED !!!!!!!!!!!!!!
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
    text_search_fields: Optional[Dict[str, Union[str, List[str]]]] = Field(
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
