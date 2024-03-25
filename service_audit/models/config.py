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
        description="Elasticsearch URL (e.g., http://elasticsearch:9200).",
    )
    index_name: str = Field(
        description="The name of the Elasticsearch Index.",
    )
    username: Optional[str] = Field(description="Elasticsearch username.")
    password: Optional[str] = Field(description="Elasticsearch password.")


class KibanaSettings(BaseModel, URLFieldValidatorMixin):
    url: HttpUrl = Field(description="Kibana URL (e.g., http://kibana:5601).")


class APISettings(BaseModel):
    host: str = Field(description="API host.")
    port: int = Field(description="API port.")
    key: Optional[str] = Field(description="API key.")


class CORSOptions(BaseModel):
    allowed_origins: Optional[List[str]] = Field(
        default=["*"],
        description="List of allowed origin URLs. Use '*' to allow all origins.",
    )
    allowed_methods: Optional[List[str]] = Field(
        default=["*"],
        description="List of allowed HTTP methods.",
    )
    allowed_headers: Optional[List[str]] = Field(
        default=["*"],
        description="List of allowed request headers. Use '*' to allow all headers.",
    )


class AppConfig(BaseModel):
    elasticsearch: ElasticsearchSettings
    kibana: KibanaSettings
    api: APISettings
    cors: Optional[CORSOptions] = Field(
        description="CORS Middleware options to apply to the API."
    )
