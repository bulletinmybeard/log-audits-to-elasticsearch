from pydantic import BaseModel, Field


class ResourceModel(BaseModel):
    type: str = Field(
        ...,
        title="Resource Type",
        description="Type of the resource that was acted upon.",
    )
    id: str = Field(
        ..., title="Resource ID", description="Unique identifier of the resource."
    )
