from typing import Any, Dict, List, Optional

from pydantic import BaseModel

from service_audit.models.resource import ResourceDetails


class ActorDetails(BaseModel):
    identifier: Optional[str]
    type: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]


class ServerInfo(BaseModel):
    hostname: Optional[str]
    vm_name: Optional[str]
    ip_address: Optional[str]


class LogEntryDetails(BaseModel):
    timestamp: Optional[str]
    event_name: Optional[str]
    actor: Optional[ActorDetails]
    action: Optional[str]
    comment: Optional[str]
    context: Optional[str]
    resource: Optional[ResourceDetails]
    operation: Optional[str]
    status: Optional[str]
    endpoint: Optional[str]
    server_details: Optional[ServerInfo]
    meta: Optional[Dict[str, Any]]


class SearchResults(BaseModel):
    hits: int
    # docs: List[ResponseLogEntry]
    docs: List[Any]
    aggs: List[Any]


class GenericResponse(BaseModel):
    status: str
    success_count: int
    failed_count: int
    failed_items: List[Dict] = []
