from typing import Optional

from pydantic import BaseModel, Field


class ActorDetails(BaseModel):
    identifier: Optional[str] = Field(
        title="Identifier", description="Unique identifier of the actor."
    )
    type: Optional[str] = Field(
        title="Type", description="Type of actor, e.g., 'user' or 'system'."
    )
    ip_address: Optional[str] = Field(
        title="IPv4 Address", description="IPv4 address of the actor."
    )
    user_agent: Optional[str] = Field(
        title="User Agent", description="User agent string of the actor's device."
    )
