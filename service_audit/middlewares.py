import os
from typing import Any, Callable

from starlette import status
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

# https://slowapi.readthedocs.io/en/latest/
# https://github.com/laurents/slowapi
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app.add_middleware(GZipMiddleware, minimum_size=1000)
# app.add_middleware(APIKeyMiddleware)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],  # Specify domains or use ["*"] for open access
#     allow_credentials=True,
#     allow_methods=["*"],  # Specify HTTP methods or use ["*"] for all methods
#     allow_headers=["*"],  # Specify headers or use ["*"] for all headers
# )

# limiter = Limiter(key_func=get_remote_address)
api_key = os.getenv("X_API_KEY")


class APIKeyMiddleware(BaseHTTPMiddleware):
    @staticmethod
    async def api_key_middleware(
        request: Request, call_next: Callable[[Request], Any]
    ) -> Response:
        expected_api_key = (
            api_key  # Ensure `api_key` is defined somewhere in your context
        )
        api_key_header = request.headers.get("X-API-Key")

        if api_key_header != expected_api_key:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid API Key"},
            )

        response = await call_next(request)
        assert isinstance(response, Response), "call_next must return a Response object"
        return response
