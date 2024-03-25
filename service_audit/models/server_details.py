from typing import Optional

from pydantic import BaseModel, Field


class ServerInfo(BaseModel):
    hostname: Optional[str] = Field(
        title="Hostname",
        description="Hostname of the server where the event occurred.",
    )
    vm_name: Optional[str] = Field(
        title="VM Name",
        description="Name of the virtual machine where the event occurred.",
    )
    ip_address: Optional[str] = Field(
        title="IP Address", description="IP address of the server."
    )
