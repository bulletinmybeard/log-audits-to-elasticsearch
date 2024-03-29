from typing import List, Optional

from pydantic import BaseModel, Field


class CORSSettings(BaseModel):
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


class APIMiddlewares(BaseModel):
    cors: CORSSettings = Field(description="CORS middleware settings")


class AppConfig(BaseModel):
    middlewares: Optional[APIMiddlewares] = Field(
        description="API Middlewares settings",
    )
