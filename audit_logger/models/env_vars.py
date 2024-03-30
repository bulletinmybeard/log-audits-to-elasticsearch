from typing import Optional

from pydantic import BaseModel, Field, HttpUrl, field_validator


class EnvVars(BaseModel):
    elastic_index_name: str = Field(...)
    elastic_url: str = Field(...)
    elastic_username: Optional[str] = Field(None)
    elastic_password: Optional[str] = Field(None)
    elastic_hosts: Optional[str] = Field(default_factory=str)
    config_file_path: str = Field(...)

    @field_validator("elastic_hosts")
    def split_hosts(cls, v):
        if not isinstance(v, str):
            raise ValueError("ELASTIC_HOSTS must be a comma-separated string")
        return [HttpUrl.build(scheme="http", host=h.strip()) for h in v.split(",") if h]
