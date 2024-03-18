from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class SearchParams(BaseModel):
    max_results: int = Field(50, ge=1, le=500)
    fields: Union[List[str], str] = "all"
    sort_by: str = Field("timestamp", description="Field to sort by")
    sort_order: str = Field("asc", description="Sort order: asc or desc")

    @field_validator("fields")
    def validate_fields(cls, values):
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
            "endpoint.keyword",
            "server_details.hostname",
            "server_details.vm_name",
            "server_details.ip_address",
        }
        if isinstance(values, list):
            if not all(item in allowed_fields for item in values):
                raise ValueError(f"Fields must consist of {allowed_fields}")
            return values
        elif values == "all":
            return list(allowed_fields)
        else:
            raise ValueError(
                "fields must be either 'all' or a list of allowed field names"
            )

    @field_validator("sort_order")
    def sort_order_valid(cls, value):
        if value not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return value
