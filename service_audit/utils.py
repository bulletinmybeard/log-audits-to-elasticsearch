from typing import Dict, List

from faker import Faker

from service_audit.models import SearchParams

fake = Faker()


def build_query_body(params: SearchParams) -> Dict:
    query_body = {
        "query": {"match_all": {}},
        "sort": [{params.sort_by: {"order": params.sort_order}}],
        "size": params.max_results,
    }
    if params.fields != "all":
        query_body["_source"] = params.fields
    return query_body


def extract_audit_logs(hits: List[Dict]) -> List[Dict]:
    return [hit["_source"] for hit in hits]


def create_bulk_operations(index_name: str, log_entries: List[Dict]) -> List[Dict]:
    operations: List[Dict] = []
    for entry in log_entries:
        operations.append({"_index": index_name, "_op_type": "index", "_source": entry})
    return operations


def generate_random_audit_log() -> Dict:
    return {
        "timestamp": fake.date_time_this_year().isoformat(),
        "event_name": fake.random_element(
            ["user_login", "data_backup", "file_access", "role_update"]
        ),
        "actor": {
            "identifier": fake.user_name(),
            "type": fake.random_element(["user", "system"]),
            "ip_address": fake.ipv4(),
            "user_agent": fake.user_agent(),
        },
        "action": fake.random_element(["create", "update", "delete", "login"]),
        "comment": fake.sentence(),
        "context": fake.random_element(
            ["user_management", "system_backup", "content_delivery", "security"]
        ),
        "resource": {
            "type": fake.random_element(
                ["user_account", "database", "blog_post", "system_file"]
            ),
            "id": fake.uuid4(),
        },
        "operation": fake.random_element(["create", "read", "update", "delete"]),
        "status": fake.random_element(["success", "failure"]),
        "endpoint": fake.uri_path(),
        "server_details": {
            "hostname": fake.hostname(),
            "vm_name": fake.word(),
            "ip_address": fake.ipv4(),
        },
        "meta": {
            # Example of dynamic meta data, adjust as needed for your use case
            "request_size": fake.random_number(digits=5),
            "response_time_ms": fake.random_int(min=1, max=1000),
        },
    }
