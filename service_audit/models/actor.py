from pydantic import BaseModel, Field


class ActorDetails(BaseModel):
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
