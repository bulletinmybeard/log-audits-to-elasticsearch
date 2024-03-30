import ipaddress
import os
import re
import traceback
from datetime import datetime
from typing import Any, Dict, List, Union

from elasticsearch import Elasticsearch, SerializationError, helpers, ConnectionError
from faker import Faker
from fastapi import HTTPException, status
from pydantic import ValidationError

from audit_logger.custom_logger import get_logger
from audit_logger.models import (
    ActorDetails,
    AuditLogEntry,
    BulkAuditLogOptions,
    GenericResponse,
    ResourceDetails,
)
from audit_logger.models.env_vars import EnvVars
from audit_logger.models.server_details import ServerDetails

fake = Faker()

logger = get_logger("audit_service")

# Regular expression to validate date strings in the format "YYYY-MM-DDTHH:MM:SSZ"
# where everything, except for the year, is optional.
DATE_FORMAT_REGEX = re.compile(
    r"""
    ^(
        (?P<year>\d{4})  # Year (YYYY)
        (
            -(?P<month>\d{2})  # Optional month (MM)
            (
                -(?P<day>\d{2})  # Optional day (DD)
                (
                    T(?P<hour>\d{2})  # Optional hour (HH)
                    (
                        :(?P<minute>\d{2})  # Optional minute (MM)
                        (
                            :(?P<second>\d{2})  # Optional second (SS)
                            (?P<timezone>[+-]\d{2}:\d{2}|Z)?  # Optional Timezone
                        )?
                    )?
                )?
            )?
        )?
    )$
""",
    re.VERBOSE,
)


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
        ip_address = str(ip_address)
        ip_obj = ipaddress.ip_address(ip_address)
        if ip_obj.version == 4:
            octets = ip_address.split(".")
            return str(".".join(octets[:2] + ["0", "0"]))
        elif ip_obj.version == 6:
            hextets = ip_address.split(":")
            anonymized_ip = ":".join(hextets[:4] + ["0", "0", "0", "0"])
            return str(ipaddress.ip_address(anonymized_ip).compressed)
    except ValueError:
        return str(ip_address)


def is_valid_ip_v4_address(ip_address: str) -> bool:
    """
    Validates an IPv4 address string.

    Args:
        ip_address (str): The IPv4 address string to validate.

    Returns:
        bool: True if the IP address is valid, False otherwise.
    """
    try:
        ipaddress.ip_address(ip_address)
        return True
    except ValueError:
        return False


def create_bulk_operations(
    index_name: str, log_entries: List[AuditLogEntry]
) -> List[Dict]:
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
        for ip_field in ["ip_address", "actor.ip_address", "server.ip_address"]:
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


def generate_audit_log_entries_with_fake_data(
    settings: BulkAuditLogOptions,
) -> List[Dict]:
    """
    Generates a random audit log entry using the Faker library.

    Returns:
    - List[Dict]: A list of audit log entries with fake data.
    """
    return [generate_log_entry().dict() for _ in range(settings.bulk_count)]


# ) -> GenericResponse:
async def process_audit_logs(
    elastic: Elasticsearch,
    elastic_index_name: str,
    log_entries: Union[AuditLogEntry, List[Union[Dict, AuditLogEntry]]]
) -> Any:
    """
    Processes a list of audit log entries by sending them to Elasticsearch using the bulk API.

    Args:
    - elastic: An instance of the Elasticsearch client.
    - elastic_index_name (str): The name of the Elasticsearch index.
    - log_entries (List[AuditLogEntry]): A list of audit log entries to be processed.

    Returns:
    - GenericResponse

    Raises:
    - HTTPException
    """

    is_bulk_operation = isinstance(log_entries, list)
    if not is_bulk_operation:
        log_entries = [log_entries.dict()]

    try:
        operations = create_bulk_operations(elastic_index_name, log_entries)
        success_count, failed = helpers.bulk(elastic, operations)
        failed_items = failed if isinstance(failed, list) else []

        if len(failed_items) > 0:
            raise HTTPException(status_code=500, detail=f"Failed to process audit logs: {str(failed_items)}")

        if is_bulk_operation:
            return GenericResponse(
                status="success",
                success_count=success_count,
            )

        return status.HTTP_201_CREATED
    except SerializationError as e:
        logger.error(
            "SerializationError: %s\nFull stack trace:\n%s", e, traceback.format_exc()
        )
        raise HTTPException(status_code=500, detail="Failed to process audit logs")
    except Exception as e:
        logger.error("Error: %s\nFull stack trace:\n%s", e, traceback.format_exc())
        raise HTTPException(status_code=500, detail="Failed to process audit logs")


def validate_date(date_str: str) -> bool:
    """
    Validates a date string against various formats
    including ISO 8601, year-month-day, and year-month.

    Args:
        date_str (str): The date string to validate.

    Returns:
        bool: True if the date string is valid, False otherwise.
    """
    if DATE_FORMAT_REGEX.match(date_str):
        for fmt in (
            "%Y-%m-%dT%H:%M:%SZ",
            "%Y-%m-%dT%H:%M:%S",
            "%Y-%m-%dT%H:%M",
            "%Y-%m-%d",
            "%Y-%m",
            "%Y",
        ):
            try:
                datetime.strptime(date_str, fmt)
                return True
            except ValueError:
                pass
    return False


def generate_log_entry() -> AuditLogEntry:
    """Create a fake audit log entry using the Faker library."""
    return AuditLogEntry(
        timestamp=fake.date_time_this_year().isoformat(),
        event_name=fake.random_element(
            ["user_login", "data_backup", "file_access", "role_update"]
        ),
        actor=ActorDetails(
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
        resource=ResourceDetails(
            type=fake.random_element(
                ["user_account", "database", "cronjob", "system_file"]
            ),
            id=fake.uuid4(),
        ),
        operation=fake.random_element(["create", "read", "update", "delete"]),
        status=fake.random_element(["success", "failure"]),
        endpoint=fake.uri_path(),
        server=ServerDetails(
            hostname=fake.hostname(),
            vm_name=fake.word(),
            ip_address=fake.ipv4(),
        ),
        meta={
            "request_size": fake.random_number(digits=5),
            "response_time_ms": fake.random_int(min=1, max=1000),
        },
    )


def load_env_vars() -> EnvVars:
    """
    Load all environment variables and validate them against the EnvVars Pydantic model.

    Returns:
        - EnvVars: The validated environment variables.
    """
    try:
        env_vars: Dict[str, Any] = {}
        for key, value in os.environ.items():
            model_field = key.lower()
            if model_field in EnvVars.__fields__:
                env_vars[model_field] = value

        logger.info("Env vars loaded.")
        return EnvVars(**env_vars)
    except ValidationError as e:
        logger.error("Env vars validation error: %s", e)
        raise
