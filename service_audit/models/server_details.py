from pydantic import BaseModel, Field


class ServerDetailsModel(BaseModel):
    hostname: str = Field(
        ...,
        title="Hostname",
        description="Hostname of the server where the event occurred.",
    )
    vm_name: str = Field(
        ...,
        title="VM Name",
        description="Name of the virtual machine where the event occurred.",
    )
    ip_address: str = Field(
        ..., title="IP Address", description="IP address of the server."
    )
