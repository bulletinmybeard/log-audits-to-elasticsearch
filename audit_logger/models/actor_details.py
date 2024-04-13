from enum import Enum
from typing import Optional

from pydantic import Field, IPvAnyAddress

from audit_logger.models.custom_base import CustomBaseModel


class ActorType(str, Enum):
    USER = "user"
    SYSTEM = "system"


class ActorDetails(CustomBaseModel):
    identifier: str = Field(
        description="Unique identifier of the actor. "
        "Can be an email address, username, etc.",
    )
    type: ActorType = Field(
        description="Type of actor, e.g., 'user' or 'system'.",
    )
    ip_address: Optional[IPvAnyAddress] = Field(
        default=None, description="IPv4 address of the actor."
    )
    user_agent: Optional[str] = Field(
        default=None,
        description="User agent string of the actor's device.",
    )
