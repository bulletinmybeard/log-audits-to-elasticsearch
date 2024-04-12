from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from audit_logger.custom_logger import get_logger
from audit_logger.models.config import AppConfig

logger = get_logger("audit_service")


def add_middleware(app: FastAPI, config: AppConfig) -> None:
    """
    Adds middleware to the FastAPI app.

    Args:
    - app: The FastAPI application instance to which the middleware will be added.
    """
    app.add_middleware(
        CORSMiddleware,
        allow_origins=config.api.middlewares.cors.allow_origins,
        allow_credentials=config.api.middlewares.cors.allow_credentials,
        allow_methods=config.api.middlewares.cors.allow_methods,
        allow_headers=config.api.middlewares.cors.allow_headers,
    )
