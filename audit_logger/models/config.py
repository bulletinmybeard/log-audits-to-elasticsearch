from typing import List, Optional

from pydantic import Field

from audit_logger.models.custom_base import CustomBaseModel


class CORSSettings(CustomBaseModel):
    allow_origins: Optional[List[str]] = Field(
        default=["*"],
        description="List of allowed origin URLs. Use '*' to allow all origins.",
    )
    allow_credentials: Optional[bool] = Field(
        default=True,
        description="",
    )
    allow_methods: Optional[List[str]] = Field(
        default=["*"],
        description="List of allowed HTTP methods.",
    )
    allow_headers: Optional[List[str]] = Field(
        default=["*"],
        description="List of allowed request headers. Use '*' to allow all headers.",
    )


class APIMiddlewares(CustomBaseModel):
    cors: CORSSettings = Field(description="CORS middleware settings")


class Authentication(CustomBaseModel):
    api_key: str = Field(description="X-API Key")


class AppConfig(CustomBaseModel):
    middlewares: Optional[APIMiddlewares] = Field(
        description="API middlewares settings",
    )
    authentication: Authentication = Field(
        description="API authentication settings",
    )
