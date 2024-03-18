import os

from fastapi import Request, status
from fastapi.responses import JSONResponse, PlainTextResponse
from starlette.middleware.base import BaseHTTPMiddleware

# https://slowapi.readthedocs.io/en/latest/
# https://github.com/laurents/slowapi
# from slowapi import Limiter, _rate_limit_exceeded_handler
# from slowapi.util import get_remote_address
# from slowapi.errors import RateLimitExceeded

# app.state.limiter = limiter
# app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# app.add_middleware(GZipMiddleware, minimum_size=1000)
# app.add_middleware(APIKeyMiddleware)
# app.add_middleware(SuppressFaviconLoggingMiddleware)
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["*"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# limiter = Limiter(key_func=get_remote_address)
api_key = os.getenv("X_API_KEY", None)


class SuppressFaviconLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/favicon.ico":
            return PlainTextResponse("", status_code=204)
        response = await call_next(request)
        return response


class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Replace 'your_api_key_here' with your actual expected API key value
        expected_api_key = api_key
        api_key_header = request.headers.get("X-API-Key")

        if api_key_header != expected_api_key:
            return JSONResponse(
                status_code=status.HTTP_403_FORBIDDEN,
                content={"detail": "Invalid API Key"},
            )

        return await call_next(request)
