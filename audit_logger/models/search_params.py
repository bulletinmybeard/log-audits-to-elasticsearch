import logging
from decimal import Decimal
from enum import Enum
from typing import Any, Dict, List, Optional, Union

from pydantic import Field, field_validator, model_validator

from audit_logger.models.custom_base import CustomBaseModel
from audit_logger.utils import is_valid_ip_v4_address, validate_date

logger = logging.getLogger("audit_logger")


class MaxResultsMixin(CustomBaseModel):
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
    NESTED_MATCH = "nested_match"


class FieldIdentifierEnum(str, Enum):
    TIMESTAMP = "timestamp"
    EVENT_NAME = "event_name"
    ACTOR = "actor"
    ACTOR_IDENTIFIER = "actor.identifier"
    ACTOR_TYPE = "actor.type"
    ACTOR_IP_ADDRESS = "actor.ip_address"
    ACTOR_USER_AGENT = "actor.user_agent"
    APPLICATION_NAME = "application_name"
    MODULE = "module"
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


class SearchFilterParams(CustomBaseModel):
    field: FieldIdentifierEnum = Field(
        default=None,
        description="",
    )
    fields: Optional[List[FieldIdentifierEnum]] = Field(
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
                if v.gte and v.lte:
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


class AggregationFilterParams(CustomBaseModel):
    range: Optional[Dict[str, Dict[str, str]]]


class SubAggregationConfig(CustomBaseModel):
    type: AggregationTypeEnum
    field: FieldIdentifierEnum


class AggregationSetup(MaxResultsMixin, CustomBaseModel):
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


class SearchParams(MaxResultsMixin, CustomBaseModel):
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
    filters_exp: Optional[List[Any]] = Field(
        default=None,
        description="Experimental filters to apply for refined search results.",
    )

    @field_validator("sort_order")
    def sort_order_valid(cls, v: Optional[SortOrderEnum]) -> Optional[SortOrderEnum]:
        if v and v not in SortOrderEnum:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return v
