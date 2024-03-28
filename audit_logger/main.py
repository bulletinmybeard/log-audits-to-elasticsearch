import os
import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, Union, cast

from fastapi import Body, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from audit_logger.config_manager import ConfigManager
from audit_logger.custom_logger import get_logger
from audit_logger.elastic import CustomElasticsearch
from audit_logger.elastic_filters import ElasticSearchQueryBuilder
from audit_logger.middlewares import add_middleware
from audit_logger.models import (
    GenericResponse,
    RandomAuditLogSettings,
    SearchParamsV2,
    SearchResults,
)
from audit_logger.utils import (
    generate_audit_log_entries_with_fake_data,
    httpurl_to_str,
    process_audit_logs,
)

config = ConfigManager.load_config(os.getenv("CONFIG_FILE_PATH"))

logger = get_logger("audit_service")

elastic_index_name = config.elasticsearch.index_name

elastic = CustomElasticsearch(
    hosts=[httpurl_to_str(url) for url in config.elasticsearch.hosts],
    http_auth=(
        (config.elasticsearch.username, config.elasticsearch.password)
        if config.elasticsearch.username and config.elasticsearch.password
        else None
    ),
)


@asynccontextmanager
async def lifespan(_: Any) -> AsyncGenerator[None, None]:
    """
    An asynchronous context manager for managing the lifecycle of the audit log API.

    Args:
        _ : Just a placeholder.
    """
    logger.info("Audit log API starting up")
    elastic.ensure_ready(elastic_index_name)
    yield
    logger.info("Audit log API shutting down")
    # Do something here...


app = FastAPI(
    debug=True,
    title="Audit Logging Service",
    summary="Service for logging security incidents and other audit events",
    description="This service provides an API for "
    "logging security incidents and other audit events.",
    version="0.5.0",
    redirect_slashes=True,
    lifespan=lifespan,
)

add_middleware(app, config)


@app.exception_handler(RequestValidationError)
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
            "option": error["loc"][1] if len(error["loc"]) > 1 else None,
        }
        for error in errors
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": simplified_errors},
    )


@app.post("/create")
async def create_audit_log_entry(audit_log: Union[Any, List[Any]] = Body(...)) -> Any:
    """
    Receives an audit log entry or a list of entries, validates them, and processes
    them to be stored in Elasticsearch.

    Args:
        audit_log (Union[AuditLogEntry, List[AuditLogEntry]]): The audit log entry or entries
            to be created. This can either be a single `AuditLogEntry` object or a list of such
            objects.

    Returns:
        CreateResponse

    Raises:
        HTTPException
    """
    return await process_audit_logs(
        elastic,
        cast(str, elastic_index_name),
        [audit_log] if not isinstance(audit_log, list) else audit_log,
    )


@app.post("/create/fake-log-entries")
async def create_fake_audit_log_entries(
    settings: RandomAuditLogSettings,
) -> GenericResponse:
    """
    Generates and stores a single random audit log entry.

    Returns:
        CreateResponse

    Raises:
        HTTPException
    """
    return await process_audit_logs(
        elastic,
        cast(str, elastic_index_name),
        generate_audit_log_entries_with_fake_data(settings),
    )


@app.post("/search")
def search_audit_log_entries(
    params: Optional[SearchParamsV2] = Body(default=None),
) -> Any:
    """
    Performs a search query against audit log entries stored in Elasticsearch based on
    a set of search parameters.

    Args:
        params (Optional[SearchParams], optional): The search parameters used to filter
            audit log entries. Defaults to an empty instance of `SearchParams` if not
            provided, resulting in a search that returns all entries.

    Returns:
        SearchResponse

    Raises:
        HTTPException
    """
    try:
        elastic_filters = ElasticSearchQueryBuilder(
            using=elastic, index=elastic_index_name
        )
        result = elastic_filters.process_parameters(params or SearchParamsV2())

        return SearchResults(
            hits=len(result["docs"]), docs=result["docs"], aggs=result["aggs"]
        )
    except Exception as e:
        logger.error("Error: %s\nFull stack trace:\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to query audit logs")


@app.get("/healthcheck", response_class=JSONResponse)
async def health_check() -> Dict[str, str]:
    """
    Health check endpoint used by Docker to check if the Elasticsearch instance/host is ready.

    Returns:
        A dictionary with a single key-value pair.

    Raises:
        HTTPException
    """
    try:
        elastic.check_health()
        return {"status": "OK"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))