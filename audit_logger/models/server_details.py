from typing import Optional

from pydantic import Field, IPvAnyAddress

from audit_logger.models.custom_base import CustomBaseModel


class ServerDetails(CustomBaseModel):
    hostname: Optional[str] = Field(
        default=None,
        description="Hostname of the server where the event occurred.",
    )
    vm_name: Optional[str] = Field(
        default=None,
        description="Name of the virtual machine where the event occurred.",
    )
    ip_address: Optional[IPvAnyAddress] = Field(
        default=None, description="IP address of the server."
    )
