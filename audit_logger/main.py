import traceback
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator, Dict, List, Optional, cast

from fastapi import Body, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from audit_logger.config_manager import ConfigManager
from audit_logger.custom_logger import get_logger
from audit_logger.elastic import CustomElasticsearch
from audit_logger.elastic_filters import ElasticSearchQueryBuilder
from audit_logger.exceptions import BulkLimitExceededError, validation_exception_handler
from audit_logger.middlewares import add_middleware
from audit_logger.models import (
    AuditLogEntry,
    BulkAuditLogOptions,
    GenericResponse,
    SearchParamsV2,
    SearchResults,
)
from audit_logger.utils import (
    generate_audit_log_entries_with_fake_data,
    load_env_vars,
    process_audit_logs,
)

logger = get_logger("audit_service")


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

    Args:
        _ : Just a placeholder.
    """
    logger.info("Audit log API starting up")
    elastic.ensure_ready(env_vars.elastic_index_name)
    yield
    logger.info("Audit log API shutting down")
    # Do something here...


app = FastAPI(
    debug=True,
    version="0.5.0",
    redirect_slashes=True,
    lifespan=lifespan,
)

app.add_exception_handler(RequestValidationError, validation_exception_handler)

add_middleware(app, app_config)


@app.post("/create")
async def create_audit_log_entry(
    audit_log: AuditLogEntry = Body(...),
) -> GenericResponse:
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
        elastic,
        cast(str, env_vars.elastic_index_name),
        [audit_log.dict()],
    )


@app.post("/create-bulk")
async def create_bulk_audit_log_entries(
    audit_logs: List[AuditLogEntry] = Body(...),
) -> GenericResponse:
    """
    Receives one or multiple audit log entries, validates them, and processes
    them to be stored in Elasticsearch.

    Args:
        audit_logs List[AuditLogEntry]: The audit log entries to be created.

    Returns:
        CreateResponse

    Raises:
        Union[HTTPException, BulkLimitExceededError]
    """
    bulk_limit = 350
    if len(audit_logs) > bulk_limit:
        raise BulkLimitExceededError(limit=bulk_limit)
    return await process_audit_logs(
        elastic,
        cast(str, env_vars.elastic_index_name),
        [dict(model.dict()) for model in audit_logs],
    )


@app.post("/create/create-bulk-auto")
async def create_fake_audit_log_entries(
    options: BulkAuditLogOptions,
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
        cast(str, env_vars.elastic_index_name),
        generate_audit_log_entries_with_fake_data(options),
    )


@app.post("/search")
def search_audit_log_entries(
    params: Optional[SearchParamsV2] = Body(default=None),
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
