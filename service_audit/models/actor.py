from typing import Optional
from enum import Enum

from pydantic import BaseModel, Field, IPvAnyAddress


class ActorType(str, Enum):
    USER = "user"
    SYSTEM = "system"


class ActorDetails(BaseModel):
    identifier: Optional[str] = Field(
        title="Identifier", description="Unique identifier of the actor. "
                                        "Can be an email address, username, etc."
    )
    type: Optional[ActorType] = Field(
        title="Type", description="Type of actor, e.g., 'user' or 'system'."
    )
    ip_address: Optional[IPvAnyAddress] = Field(
        title="IPv4 Address", description="IPv4 address of the actor."
    )
    user_agent: Optional[str] = Field(
        title="User Agent", description="User agent string of the actor's device."
    )
