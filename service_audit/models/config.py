from typing import List, Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class URLFieldValidatorMixin:
    @field_validator("url")
    def parse_url(cls, v: str) -> str:
        """
        Validator to parse the URL and validate its format.
        """
        url_str = str(v)
        if url_str.startswith("http://") or url_str.startswith("https://"):
            return v
        else:
            raise ValueError("URL must start with 'http://' or 'https://'.")


class ElasticsearchSettings(BaseModel, URLFieldValidatorMixin):
    url: HttpUrl = Field(
        ...,
        title="Elasticsearch URL",
        description="Elasticsearch URL (e.g., http://elasticsearch:9200).",
    )
    index_name: str = Field(
        ...,
        title="Elasticsearch Index",
        description="The name of the Elasticsearch Index.",
    )
    username: Optional[str] = Field(
        ..., title="Elasticsearch username", description="Elasticsearch username."
    )
    password: Optional[str] = Field(
        ..., title="Elasticsearch password", description="Elasticsearch password."
    )


class KibanaSettings(BaseModel, URLFieldValidatorMixin):
    url: HttpUrl = Field(
        ..., title="Kibana URL", description="Kibana URL (e.g., http://kibana:5601)."
    )


class APISettings(BaseModel):
    host: str = Field(..., title="API host", description="API host.")
    port: int = Field(..., title="API port", description="API port.")
    key: Optional[str] = Field(..., title="API key", description="API key.")


class CORSOptions(BaseModel):
    allowed_origins: Optional[List[str]] = Field(
        default=["*"],
        title="Allowed Origins",
        description="List of allowed origin URLs. Use '*' to allow all origins.",
    )
    allowed_methods: Optional[List[str]] = Field(
        default=["*"],
        title="Allowed Methods",
        description="List of allowed HTTP methods.",
    )
    allowed_headers: Optional[List[str]] = Field(
        default=["*"],
        title="Allowed Headers",
        description="List of allowed request headers. Use '*' to allow all headers.",
    )


class AppConfig(BaseModel):
    elasticsearch: ElasticsearchSettings
    kibana: KibanaSettings
    api: APISettings
    cors: CORSOptions
