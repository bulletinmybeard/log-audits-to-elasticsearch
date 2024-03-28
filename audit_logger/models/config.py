from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class ElasticsearchSettings(BaseModel):
    hosts: List[HttpUrl] = Field(
        description="Elasticsearch URL (e.g., [http://elasticsearch:9200]).",
    )
    index_name: str = Field(
        description="The name of the Elasticsearch Index.",
    )
    username: Optional[str] = Field(description="Elasticsearch username.")
    password: Optional[str] = Field(description="Elasticsearch password.")

    @field_validator("hosts")
    def validate_urls(cls, values: List[str]) -> List[str]:
        """
        Validator to parse each URL in the list and validate its format.
        Each URL must start with 'http://' or 'https://'.
        """
        urls = []
        for v in values:
            url_str = str(v)
            if url_str.startswith("http://") or url_str.startswith("https://"):
                urls.append(url_str)
            else:
                raise ValueError("Each URL must start with 'http://' or 'https://'.")
        return urls


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


class APISettings(BaseModel):
    middlewares: Optional[APIMiddlewares] = Field(
        default=None,
        title="API Middlewares settings",
        description="API Middlewares settings",
    )


class AppConfig(BaseModel):
    elasticsearch: ElasticsearchSettings
    api: APISettings
