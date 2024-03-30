from typing import Any

from pydantic import BaseModel, Extra


class CustomBaseModel(BaseModel):
    def __init__(self, **kwargs: Any) -> None:
        super().__init__(**kwargs)

    # Forbid extra fields and raise an exception if any are found.
    class Config:
        extra = Extra.forbid
