from datetime import datetime
from enum import Enum
from typing import List, Optional, Union

from pydantic import BaseModel, Field, field_validator


class SearchParams(BaseModel):
    max_results: int = Field(50, ge=1, le=500)
    fields: Union[List[str], str] = "all"
    sort_by: str = "timestamp"
    sort_order: str = "asc"

    @field_validator("fields")
    def validate_fields(cls, values):
        allowed_fields = {
            "timestamp",
            "service",
            "platform",
            "action",
            "user",
            "game_id",
            "service",
            "action",
        }
        if isinstance(values, list):
            if not all(item in allowed_fields for item in values):
                raise ValueError(f"Fields must consists of {allowed_fields}")
            return values
        elif values == "all":
            return list(
                allowed_fields
            )  # Convert to list to standardize the output format
        else:
            raise ValueError(
                "fields must be either 'all' or a list of allowed field names"
            )

    @field_validator("sort_order")
    def sort_order_valid(cls, value):
        if value not in ["asc", "desc"]:
            raise ValueError("sort_order must be 'asc' or 'desc'")
        return value
