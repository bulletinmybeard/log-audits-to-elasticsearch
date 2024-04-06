import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, cast

from fastapi import Body, Depends, FastAPI, HTTPException, status
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.security import APIKeyHeader

from audit_logger.config_manager import ConfigManager
from audit_logger.custom_logger import get_logger
from audit_logger.elastic import CustomElasticsearch
from audit_logger.elastic_filters import ElasticSearchQueryBuilder
from audit_logger.exceptions import (
    BulkLimitExceededError,
    validation_exception_handler,
    value_error_handler,
)
from audit_logger.middlewares import add_middleware
from audit_logger.models import (
    AuditLogEntry,
    BulkAuditLogOptions,
    SearchParams,
    SearchResults,
)
from audit_logger.utils import (
    generate_audit_log_entries_with_fake_data,
    load_env_vars,
    process_audit_logs,
)

logger = get_logger("audit_logger")


env_vars = load_env_vars()
app_config = ConfigManager.load_config(env_vars.config_file_path)

elastic = CustomElasticsearch(
    hosts=[f"{env_vars.elastic_url}"],
    http_auth=(
        (env_vars.elastic_username, env_vars.elastic_password)
        if env_vars.elastic_username and env_vars.elastic_password
        else None
    ),
)


@asynccontextmanager
async def lifespan(_: Any) -> AsyncGenerator[None, None]:
    """
    An asynchronous context manager for managing the lifecycle of the audit log API.
    """
    logger.info("Audit log API starting up")
    elastic.ensure_ready(env_vars.elastic_index_name)
    yield
    logger.info("Audit log API shutting down")


app = FastAPI(
    debug=True,
    version="1.0.0",
    redirect_slashes=True,
    lifespan=lifespan,
)

api_key_header = APIKeyHeader(name="X-API-Key")

app.add_exception_handler(RequestValidationError, validation_exception_handler)
app.add_exception_handler(ValueError, value_error_handler)

add_middleware(app, app_config)


async def verify_api_key(api_key: str = Depends(api_key_header)) -> str:
    if api_key != app_config.authentication.api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API-Key"
        )
    return api_key


@app.post(
    "/create", dependencies=[Depends(verify_api_key)], response_class=JSONResponse
)
async def create_audit_log_entry(audit_log: AuditLogEntry = Body(...)) -> Any:
    """
    Receives an audit log entry, validates it, and processes
    it to be stored in Elasticsearch.

    Args:
        audit_log AuditLogEntry: The audit log entry to be created.

    Returns:
        CreateResponse

    Raises:
        HTTPException
    """
    return await process_audit_logs(
        elastic, cast(str, env_vars.elastic_index_name), audit_log
    )


@app.post(
    "/create-bulk", dependencies=[Depends(verify_api_key)], response_class=JSONResponse
)
async def create_bulk_audit_log_entries(
    audit_logs: List[AuditLogEntry] = Body(...),
) -> Any:
    """
    Receives one or multiple audit log entries, validates them, and processes
    them to be stored in Elasticsearch.

    Args:
        audit_logs List[AuditLogEntry]: The audit log entries to be created.

    Returns:
        CreateResponse
    """
    bulk_limit = 350
    if len(audit_logs) > bulk_limit:
        raise BulkLimitExceededError(limit=bulk_limit)

    try:
        return await process_audit_logs(
            elastic,
            cast(str, env_vars.elastic_index_name),
            [dict(model.dict()) for model in audit_logs],
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error: %s\nFull stack trace:\n%s", e, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process audit log entries.",
        ) from e


@app.post(
    "/create/create-bulk-auto",
    dependencies=[Depends(verify_api_key)],
    response_class=JSONResponse,
)
async def create_random_audit_log_entries(
    options: BulkAuditLogOptions,
) -> Any:
    """
    Generates and stores a single random audit log entry.

    Returns:
        CreateResponse
    """
    try:
        return await process_audit_logs(
            elastic,
            cast(str, env_vars.elastic_index_name),
            generate_audit_log_entries_with_fake_data(options),
        )
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error("Error: %s\nFull stack trace:\n%s", e, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to process audit log entries.",
        ) from e


@app.post("/search", dependencies=[Depends(verify_api_key)])
def search_audit_log_entries(
    params: Optional[SearchParams] = Body(default=None),
) -> SearchResults:
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
            using=elastic, index=env_vars.elastic_index_name
        )
        result = elastic_filters.process_parameters(params or SearchParams())
        return SearchResults(
            hits=len(result["docs"]), docs=result["docs"], aggs=result["aggs"]
        )
    except ValueError as ve:
        detail_message = f"Invalid parameter value: {ve}"
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=detail_message
        ) from ve
    except Exception as e:
        logger.error("Error: %s\nFull stack trace:\n%s", e, traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to query audit logs",
        )


@app.get("/health", response_class=JSONResponse)
async def health_check() -> Dict[str, str]:
    """
    Simple health check endpoint.
    """
    return {
        "status": "OK",
    }
