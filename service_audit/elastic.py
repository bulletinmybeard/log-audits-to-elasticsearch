from elasticsearch import Elasticsearch
from elasticsearch.exceptions import (
    AuthenticationException,
    AuthorizationException,
    ConnectionError,
    NotFoundError,
    TransportError,
)


class CustomElasticsearch(Elasticsearch):
    def __init__(self, hosts=None, **kwargs):
        # Store hosts for potential re-instantiation by helpers
        self._hosts = hosts or ["localhost"]
        super().__init__(hosts=self._hosts, **kwargs)

    # Optional: Override the options() method if needed to ensure correct client re-instantiation
    def options(self, **kwargs):
        # Return a new instance of the custom client with the same hosts and updated kwargs
        return type(self)(hosts=self._hosts, **kwargs)

    def check_health(self) -> None:
        """
        Checks if Elasticsearch service is reachable.
        """
        try:
            if not self.ping():
                raise ValueError("[Elastic] Service is not reachable")
        except (
            ConnectionError,
            TransportError,
            AuthorizationException,
            AuthenticationException,
        ) as e:
            # Raise a more generic error but log the specific error message
            raise ConnectionError(f"[Elastic] connection/authentication failed: {e}")

    def check_index_exists(self, index_name: str) -> None:
        """
        Checks if the specified index exists.
        """
        try:
            if not self.indices.exists(index=index_name):
                raise NotFoundError(
                    meta={"index": index_name},
                    body=f"[Elastic] index '{index_name}' does not exist",
                    # message=f"[Elastic] index '{index_name}' does not exist",
                )
        except NotFoundError as e:
            raise e
        except AuthorizationException as e:
            raise ValueError(
                f"[Elastic] Authorization error accessing index '{index_name}': {e}"
            )
        except AuthenticationException as e:
            raise ValueError(f"[Elastic] Authentication error: {e}")

    def ensure_ready(self, index_name: str):
        """
        Ensures Elasticsearch service is reachable and the specified index exists.
        """
        self.check_health()  # Check Elasticsearch service reachability
        self.check_index_exists(index_name)  # Check if the index exists
