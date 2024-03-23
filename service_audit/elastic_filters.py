from service_audit.custom_logger import get_logger
import traceback
from typing import Any, Dict

from elasticsearch import Elasticsearch
from elasticsearch_dsl import A, Q, Search
from fastapi import HTTPException

from service_audit.models import SearchParams

logger = get_logger('audit_service')


class QueryFilterElasticsearch(Search):
    elastic_index_name: str

    def __init__(self, using: Elasticsearch, index: str, **kwargs):
        super(QueryFilterElasticsearch, self).__init__(
            using=using, index=index, **kwargs
        )
        self.elastic_index_name = index

    def apply_filters(self, params):
        s = self

        # Either exclude or include fields from the search results.
        if params.include_fields and params.exclude_fields is None:
            s = s.source(includes=params.include_fields)
        elif params.include_fields is None and params.exclude_fields:
            s = s.source(excludes=params.exclude_fields)

        # Performs text searches by utilizing a given set of parameters
        # and iterating over each key-value pair using the key to determine
        # whether a simple text or nested query should be executed.
        if params.text_search_fields:
            for key, value in params.text_search_fields.items():
                if "." in key:
                    path = key.split(".")[0]
                    field = key.split(".")[1]
                    s = s.query(
                        "nested",
                        path=path,
                        query=Q("match", **{f"{path}__{field}": value}),
                    )
                else:
                    s = s.query("match", **{key: value})

        # Apply date range filtering with `date_range_start` and `date_range_end`
        # start_date = datetime.fromisoformat(params.date_range_start)
        # end_date = datetime.fromisoformat(params.date_range_end)
        if params.date_range_start:
            s = s.filter(
                "range",
                timestamp={
                    "gte": params.date_range_start,
                    "lte": params.date_range_end or "now",
                },
            )

        if params.aggregations:
            # s.aggs.bucket('by_sn', 'terms', field='event_name', order={'avg_action': 'desc'}).metric('avg_action', 'avg', field='action') # noqa E501
            for bucket, field in params.aggregations.items():
                if isinstance(field, str):
                    s.aggs.bucket(bucket, A("terms", field=field))
                elif isinstance(field, dict):
                    pass
                pass

        # Set the maximum number of documents to return and ensure that `response.hits.total.value`
        # consists of the total number of documents,
        # which is typically limited to 10.000 by default.
        s = s.extra(from_=0, size=params.max_results, track_total_hits=True)

        # Sort per default by `timestamp` in descending order.
        s.sort(params.sort_by, {"order": params.sort_order})

        response = s.execute()

        if not response.success():
            raise HTTPException(
                status_code=400, detail="[QueryFilterElasticsearch] Search failed."
            )

        return {
            "docs": [hit.to_dict() for hit in response.hits],
            "aggs": [agg.to_dict() for agg in response.aggs],
            "index_size": response.hits.total.value,
        }

    def search_audit_logs(self, params: SearchParams) -> Dict[str, Any]:
        """
        Performs an Elasticsearch search operation based on the provided parameters.

        Args:
            params (SearchParams): The search parameters for the operation.

        Returns:
            Dict[str, Any]: The search results in a transformed format.

        Raises:
            HTTPException: If the search operation fails.
        """
        try:
            return self.apply_filters(params)
        except Exception as e:
            logger.error(f"Error: {e}\nFull stack trace:\n{traceback.format_exc()}")
            raise HTTPException(status_code=500, detail="Failed to query audit logs")
