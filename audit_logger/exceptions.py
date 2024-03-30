from typing import Any

from fastapi import HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def validation_exception_handler(
    _: Any, exc: RequestValidationError
) -> JSONResponse:
    """
    Handles validation errors.

    Args:
        _ : The request object which is not used in this handler but it's part of the
            signature required by FastAPI.
        exc : The `RequestValidationError` instance containing details about the validation
              checks.

    Returns:
        A `JSONResponse` object with a 422 status code and a json body containing the simplified
        list of validation errors.
    """
    errors = exc.errors()
    simplified_errors = [
        {
            "msg": error["msg"],
            "type": error["type"],
            "loc": error["loc"][0],
            "option": error["loc"][1] if len(error["loc"]) > 1 else None,
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": simplified_errors},
    )


class BulkLimitExceededError(HTTPException):
    def __init__(self, limit: int):
        super().__init__(
            status_code=400,
            detail=f"The maximum number of items allowed in a bulk operation is {limit}.",
        )
