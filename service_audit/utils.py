import ipaddress
import logging
import traceback
from typing import Any, Dict, List

from elasticsearch import helpers
from faker import Faker
from fastapi import HTTPException
from pydantic import ValidationError

from service_audit.models import (
    ActorModel,
    AuditLogEntry,
    CreateResponse,
    ResourceModel,
    SearchParams,
    ServerDetailsModel,
)

fake = Faker()

logger = logging.getLogger(__name__)


def build_query_body(params: SearchParams) -> Dict[str, Any]:
    query_body: Dict[str, Any] = {
        "query": {"bool": {"must": [], "must_not": [], "should": []}},
        "sort": [{params.sort_by: {"order": params.sort_order}}],
        "size": params.max_results,
    }

    if params.text_search_fields:
        for field, query in params.text_search_fields.items():
            query_body["query"]["bool"]["must"].append({"match": {field: query}})

    if params.search_query:
        query_body["query"]["bool"]["must"].append(
            {"query_string": {"query": params.search_query}}
        )

    # Hmm...
    # if params.search_query and params.text_search_fields:
    #     must_queries.append({
    #         "multi_match": {
    #             "query": params.search_query,
    #             "fields": params.text_search_fields
    #         }
    #     })

    if params.date_range_start and params.date_range_end:
        query_body["query"]["bool"]["must"].append(
            {
                "range": {
                    "timestamp": {
                        "gte": params.date_range_start,
                        "lte": params.date_range_end,
                    }
                }
            }
        )

    if params.exact_matches:
        for field, value in params.exact_matches.items():
            if isinstance(value, list):
                query_body["query"]["bool"]["must"].append({"terms": {field: value}})
            else:
                query_body["query"]["bool"]["must"].append({"term": {field: value}})

    if params.fields != "all":
        query_body["_source"] = params.fields

    if params.exclusions:
        for field, value in params.exclusions.items():
            if isinstance(value, list):
                query_body["query"]["bool"]["must_not"].append(
                    {"terms": {field: value}}
                )
            else:
                query_body["query"]["bool"]["must_not"].append({"term": {field: value}})

    # # Include nested fields logic
    # if params.include_nested:
    #     query_body["_source"] = {
    #         "includes": ["*", "actor.*", "resource.*", "server_details.*"]
    #     }
    #     ## Add a generic nested query structure; specifics would depend on input
    #     # nested_queries: List[Any] = [{
    #     #     "nested": {
    #     #         "path": "actor",
    #     #         "query": {
    #     #             "bool": {
    #     #                 "must": [
    #     #                     # Example condition - match a specific actor type
    #     #                     {"match": {"actor.type": "user"}}
    #     #                 ]
    #     #             }
    #     #         }
    #     #     }
    #     # }]
    #     #
    #     # # Example: Searching within the actor nested object
    #     #
    #     # # Incorporate nested queries into the main query body
    #     # if not query_body["query"]["bool"].get("must"):
    #     #     query_body["query"]["bool"]["must"] = []
    #     # query_body["query"]["bool"]["must"].extend(nested_queries)

    if params.min_should_match:
        query_body["query"]["bool"]["minimum_should_match"] = params.min_should_match

    if params.aggregations:
        query_body["aggs"] = params.aggregations

    return query_body


def anonymize_ip_address(ip_address: str) -> str:
    """
    Anonymizes an IP address by replacing the last segments with zeros.
    For IPv4 addresses, the last two octets are set to zero.
    For IPv6 addresses, the last four hextets are replaced with zeros,
    and the address is then compressed to its shortest form.
    If the input is not a valid IP address, it is returned unchanged.

    Args:
    - ip_address (str): The IP address to anonymize.

    Returns:
    - str: The anonymized IP address.
    """
    try:
        ip_obj = ipaddress.ip_address(ip_address)
        if ip_obj.version == 4:
            octets = ip_address.split(".")
            return ".".join(octets[:2] + ["0", "0"])
        elif ip_obj.version == 6:
            hextets = ip_address.split(":")
            anonymized_ip = ":".join(hextets[:4] + ["0", "0", "0", "0"])
            return ipaddress.ip_address(anonymized_ip).compressed
    except ValueError:
        return ip_address


def create_bulk_operations(index_name: str, log_entries: List[Dict]) -> List[Dict]:
    """
    This bulk helper function prepares a list of operations for the Elasticsearch bulk API
    based on the provided log entries.

    Args:
    - index_name (str): The name of the Elasticsearch index
    - log_entries (List[Dict]): A list of log entry dictionaries to be processed.

    Returns:
    - List[Dict]: A list of dictionaries formatted for the Elasticsearch bulk API.
    """
    operations: List[Dict] = []
    for entry in log_entries:
        for ip_field in ["ip_address", "actor.ip_address", "server_details.ip_address"]:
            ip_path = ip_field.split(".")
            current_level = entry
            for part in ip_path[:-1]:
                if part in current_level:
                    current_level = current_level[part]
                else:
                    break
            if ip_path[-1] in current_level:
                current_level[ip_path[-1]] = anonymize_ip_address(
                    current_level[ip_path[-1]]
                )
        operations.append({"_index": index_name, "_op_type": "index", "_source": entry})
    return operations


def generate_random_audit_log() -> AuditLogEntry:
    """
    Generates a random audit log entry using the Faker library.

    Returns:
    - AuditLogEntry: A randomly generated audit log entry.
    """
    return AuditLogEntry(
        timestamp=fake.date_time_this_year().isoformat(),
        event_name=fake.random_element(
            ["user_login", "data_backup", "file_access", "role_update"]
        ),
        actor=ActorModel(
            identifier=fake.random_element(["j.doe", "j.dot", "a.smith", "s.jones"]),
            type=fake.random_element(["user", "system"]),
            ip_address=fake.ipv4(),
            user_agent=fake.user_agent(),
        ),
        action=fake.random_element(["create", "update", "delete", "login"]),
        comment=fake.sentence(),
        context=fake.random_element(
            ["user_management", "system_backup", "content_delivery", "security"]
        ),
        resource=ResourceModel(
            type=fake.random_element(
                ["user_account", "database", "cronjob", "system_file"]
            ),
            id=fake.uuid4(),
        ),
        operation=fake.random_element(["create", "read", "update", "delete"]),
        status=fake.random_element(["success", "failure"]),
        endpoint=fake.uri_path(),
        server_details=ServerDetailsModel(
            hostname=fake.hostname(),
            vm_name=fake.word(),
            ip_address=fake.ipv4(),
        ),
        meta={
            "request_size": fake.random_number(digits=5),
            "response_time_ms": fake.random_int(min=1, max=1000),
        },
    )


async def process_audit_logs(
    elastic: Any, elastic_index_name: str, log_entries: List[Dict]
) -> CreateResponse:
    """
    Processes a list of audit log entries by sending them to Elasticsearch using the bulk API.

    Args:
    - es: An instance of the Elasticsearch client.
    - elastic_index_name (str): The name of the Elasticsearch index.
    - log_entries (List[Dict]): A list of audit log entries to be processed.

    Returns:
    - CreateResponse

    Raises:
    - HTTPException
    """
    try:
        operations = create_bulk_operations(elastic_index_name, log_entries)
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
        logger.error(f"Error: {e}\nFull stack trace:\n{traceback.format_exc()}")
        raise HTTPException(status_code=500, detail="Failed to process audit logs")
