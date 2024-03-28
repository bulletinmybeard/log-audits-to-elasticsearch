from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, IPvAnyAddress


class ActorType(str, Enum):
    USER = "user"
    SYSTEM = "system"


class ActorDetails(BaseModel):
    identifier: Optional[str] = Field(
        default=None,
        description="Unique identifier of the actor. "
        "Can be an email address, username, etc.",
    )
    type: Optional[ActorType] = Field(
        default=None,
        description="Type of actor, e.g., 'user' or 'system'.",
    )
    ip_address: Optional[IPvAnyAddress] = Field(
        default=None, description="IPv4 address of the actor."
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="User agent string of the actor's device.",
    )
