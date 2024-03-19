import logging
import os
import traceback
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Dict, List, Optional, Union

from elasticsearch import Elasticsearch
from fastapi import Body, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse

from service_audit.models import (
    AuditLogEntry,
    CreateResponse,
    ResponseLogEntry,
    SearchResponse,
)
from service_audit.utils import (
    SearchParams,
    build_query_body,
    generate_random_audit_log,
    process_audit_logs,
)

environment = os.getenv("ENVIRONMENT", "development")
api_dir = os.getenv("API_DIR")
log_level = (os.getenv("LOG_LEVEL", "")).upper()

elasticsearch_host = os.getenv("ELASTICSEARCH_HOST")
elastic_index_name = os.getenv("ELASTIC_INDEX_NAME")
elastic_username = os.getenv("ELASTIC_USERNAME")
elastic_password = os.getenv("ELASTIC_PASSWORD")

logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level, logging.ERROR))
logger.addHandler(logging.StreamHandler())

es = Elasticsearch(
    [elasticsearch_host],
    # http_auth=(elastic_username, elastic_password)
)


@asynccontextmanager
async def lifespan(_) -> AbstractAsyncContextManager[Any]:
    """
    An asynchronous context manager for managing the lifecycle of the audit log API.

    Args:
        _ : Just a placeholder.
    """
    logger.info("Audit log API starting up")
    # Do something here...
    yield
    logger.info("Audit log API shutting down")
    # Do something here...


app = FastAPI(
    debug=True,
    title="Audit Log Service",
    summary="Service for logging security incidents and other audit events",
    description="This service provides an API for "
    "logging security incidents and other audit events.",
    version="0.1.0",
    redirect_slashes=True,
    lifespan=lifespan,
)


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
        {"msg": error["msg"], "type": error["type"]} for error in errors
    ]
    return JSONResponse(
        status_code=422,
        content={"detail": simplified_errors},
    )


@app.post("/create")
async def create_audit_log(
    audit_log: Union[AuditLogEntry, List[AuditLogEntry]] = Body(...)
) -> CreateResponse:
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
    log_entries = [audit_log] if not isinstance(audit_log, list) else audit_log
    validated_logs = [entry.dict() for entry in log_entries]
    return await process_audit_logs(es, elastic_index_name, validated_logs)


@app.post("/create-random")
async def create_random_audit_log() -> CreateResponse:
    """
    Generates and stores a single random audit log entry.

    Returns:
        CreateResponse

    Raises:
        HTTPException
    """
    random_log = generate_random_audit_log().dict()
    return await process_audit_logs(es, elastic_index_name, [random_log])


@app.post("/search")
async def search_audit_log_entries(
    params: Optional[SearchParams] = Body(default=None),
) -> SearchResponse:
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
        query_body = build_query_body(params or SearchParams())
        result = es.search(index=f"{elastic_index_name}*", body=query_body)
        hits = result["hits"]["hits"]
        audit_logs = [ResponseLogEntry(**log["_source"]) for log in hits]

        return SearchResponse(hits=len(hits), logs=audit_logs)
    except Exception as e:
        logger.error(f"Error: {e}\nFull stack trace:\n{traceback.format_exc()}")
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
    if es.ping():
        return {"status": "OK"}
    else:
        raise HTTPException(
            status_code=500, detail="Elasticsearch server is not reachable"
        )
