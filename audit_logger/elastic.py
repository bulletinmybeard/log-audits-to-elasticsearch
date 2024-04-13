import traceback

from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConnectionError,
    NotFoundError,
    TransportError,
)

from audit_logger.custom_logger import get_logger

logger = get_logger("audit_logger")


class CustomElasticsearch(Elasticsearch):

    def check_health(self) -> None:
        """
        Checks if Elasticsearch service is reachable.
        """
        try:
            if not self.ping():
                raise ValueError("[Elastic] Service is not reachable")
            else:
                logger.info("[Elastic] Service is reachable")
        except (
            ConnectionError,
            TransportError,
            AuthorizationException,
            AuthenticationException,
        ) as e:
            logger.error(
                "[Elastic] connection/authentication error: %s\nFull stack trace:\n%s",
                e,
                traceback.format_exc(),
            )
            raise ConnectionError(f"[Elastic] connection/authentication failed: {e}")

    def check_index_exists(self, index_name: str) -> None:
        """
        Checks if the specified index exists.
        """
        try:
            if not self.indices.exists(index=index_name):
                raise NotFoundError(
                    meta={"index": index_name},  # type: ignore
                    body=f"[Elastic] index '{index_name}' does not exist",
                )  # type: ignore
        except NotFoundError as e:
            logger.error(
                "[Elastic] Not found error: %s\nFull stack trace:\n%s",
                e,
                traceback.format_exc(),
            )
            raise e
        except AuthorizationException as e:
            logger.error(
                "[Elastic] Authorization error: %s\nFull stack trace:\n%s",
                e,
                traceback.format_exc(),
            )
            raise ValueError(
                f"[Elastic] Authorization error accessing index '{index_name}': {e}"
            )
        except AuthenticationException as e:
            raise ValueError(f"[Elastic] Authentication error: {e}")

    def ensure_ready(self, index_name: str) -> None:
        """
        Ensures Elasticsearch service is reachable and the specified index exists.
        """
        self.check_health()
        self.check_index_exists(index_name)
