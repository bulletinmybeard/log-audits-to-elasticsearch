import logging
import os
from contextlib import AbstractAsyncContextManager, asynccontextmanager
from typing import Any, Dict, List, Optional, Union

from elasticsearch import Elasticsearch, helpers
from fastapi import Body, FastAPI, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from service_audit.models import (
    AuditLogEntry,
    CreateResponse,
    ResponseLogEntry,
    SearchResponse,
)
from service_audit.utils import (
    SearchParams,
    build_query_body,
    create_bulk_operations,
    generate_random_audit_log,
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
    try:
        if not isinstance(audit_log, list):
            audit_log = [audit_log]

        validated_logs = [entry.dict() for entry in audit_log]

        operations = create_bulk_operations(elastic_index_name, validated_logs)
        success_count, failed = helpers.bulk(es, operations)
        failed_count = len(failed) if isinstance(failed, list) else failed
        failed_items = failed if isinstance(failed, list) else []

        return CreateResponse(
            status="success",
            success_count=success_count,
            failed_count=failed_count,
            failed_items=failed_items,
        )
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Failed to create audit logs")


@app.post("/create-random")
async def create_random_audit_log() -> CreateResponse:
    try:
        operations = create_bulk_operations(
            elastic_index_name, [generate_random_audit_log().dict()]
        )
        success_count, failed = helpers.bulk(es, operations)
        failed_count = len(failed) if isinstance(failed, list) else failed
        failed_items = failed if isinstance(failed, list) else []

        return CreateResponse(
            status="success",
            success_count=success_count,
            failed_count=failed_count,
            failed_items=failed_items,
        )
    except ValidationError as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Failed to create audit log")


@app.post("/search")
async def search_audit_log_entries(
    params: Optional[SearchParams] = Body(default=None),
) -> SearchResponse:
    try:
        query_body = build_query_body(params or SearchParams())
        result = es.search(index=f"{elastic_index_name}*", body=query_body)
        hits = result["hits"]["hits"]
        audit_logs = [ResponseLogEntry(**log["_source"]) for log in hits]

        return SearchResponse(hits=len(hits), logs=audit_logs)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=500, detail="Failed to query audit logs")


@app.get("/healthcheck", response_class=JSONResponse)
async def health_check() -> Dict[str, str]:
    if es.ping():
        return {"status": "OK"}
    else:
        raise HTTPException(
            status_code=500, detail="Elasticsearch server is not reachable"
        )
