from typing import Any, Dict, List, Optional

from pydantic import BaseModel


class ResponseActor(BaseModel):
    identifier: Optional[str]
    type: Optional[str]
    ip_address: Optional[str]
    user_agent: Optional[str]


class ResponseResource(BaseModel):
    type: Optional[str]
    id: Optional[str]


class ResponseServerDetails(BaseModel):
    hostname: Optional[str]
    vm_name: Optional[str]
    ip_address: Optional[str]


class ResponseLogEntry(BaseModel):
    timestamp: Optional[str]
    event_name: Optional[str]
    actor: Optional[ResponseActor]
    action: Optional[str]
    comment: Optional[str]
    context: Optional[str]
    resource: Optional[ResponseResource]
    operation: Optional[str]
    status: Optional[str]
    endpoint: Optional[str]
    server_details: Optional[ResponseServerDetails]
    meta: Optional[Dict[str, Any]]


class SearchResponse(BaseModel):
    hits: int
    logs: List[ResponseLogEntry]


class CreateResponse(BaseModel):
    status: str
    success_count: int
    failed_count: int
    failed_items: List[Dict] = []
