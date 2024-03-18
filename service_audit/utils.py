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


def extract_audit_logs_with_id(hits: List[Dict]) -> List[Dict]:
    audit_logs = []
    for hit in hits:
        source_with_id = hit["_source"].copy()
        source_with_id["doc_id"] = hit["_id"]
        audit_logs.append(source_with_id)
    return audit_logs


def extract_audit_logs(hits: List[Dict]) -> List[Dict]:
    return [hit["_source"] for hit in hits]


def create_bulk_operations(index_name, log_entries):
    operations = []
    for entry in log_entries:
        operations.append({"_index": index_name, "_op_type": "index", "_source": entry})
    return operations


def generate_random_audit_log() -> Dict:
    return {}
