from typing import Any

from fastapi import HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse


async def value_error_handler(_: Any, exc: Exception) -> JSONResponse:
    """
    Handles ValueError exceptions raised during request processing.

    Args:
        _ : The request object which is not used in this handler but it's part of the
            signature required by FastAPI.
        exc: The `ValueError` instance raised.

    Returns:
        A `JSONResponse` object with a 400 status code and a json body detailing the error.
    """
    if isinstance(exc, ValueError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )
    else:
        raise exc


async def validation_exception_handler(_: Any, exc: Exception) -> JSONResponse:
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
    if isinstance(exc, RequestValidationError):
        errors = exc.errors()
        simplified_errors = [
            {
                "msg": error["msg"],
                "type": error["type"],
                "field": error["loc"][1] if len(error["loc"]) > 1 else None,
            }
            for error in errors
        ]
        return JSONResponse(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            content={"detail": simplified_errors},
        )
    else:
        raise exc


class BulkLimitExceededError(HTTPException):
    """
    Raised when a bulk operation exceeds the maximum number of items allowed in a bulk operation.
    """

    def __init__(self, limit: int) -> None:
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"The maximum number of items allowed in a bulk operation is {limit}.",
        )
