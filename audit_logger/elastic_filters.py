from typing import Any, Dict, List

from elasticsearch import Elasticsearch
from elasticsearch_dsl import A, Q, Search
from fastapi import HTTPException

from audit_logger.custom_logger import get_logger
from audit_logger.models import (
    AggregationSetup,
    AggregationTypeEnum,
    FieldIdentifierEnum,
    FilterTypeEnum,
    SearchFilterParams,
    SearchParamsV2,
)

logger = get_logger("audit_service")


class ElasticSearchQueryBuilder(Search):
    elastic_index_name: str

    def __init__(self, using: Elasticsearch, index: str, **kwargs):
        super(ElasticSearchQueryBuilder, self).__init__(
            using=using, index=index, **kwargs
        )
        self.elastic_index_name = index

    def process_parameters(self, params: SearchParamsV2) -> Dict[str, Any]:
        s = self

        # Set the number of documents to be returned.
        s = s.extra(from_=0, size=params.max_results, track_total_hits=True)

        # Sort the documents based on the `sort_by` (field) and sort_order (asc/desc).
        s = self.sort_order(s, params)

        # Select the fields to be returned.
        if params.fields:
            s = self.select_fields(s, params)

        # Process all given filters.
        if params.filters:
            s = self.process_filters(s, params.filters)

        # Process all given aggregations.
        if params.aggs:
            s = self.process_aggregations(s, params.aggs)

        # Execute the search query.
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

    @staticmethod
    def sort_order(s: Search, params: SearchParamsV2) -> Search:
        """Sort the documents based on the `sort_by` (field) and sort_order (asc/desc)."""
        return s.sort({params.sort_by: {"order": params.sort_order}})

    @staticmethod
    def select_fields(s: Search, params: SearchParamsV2) -> Search:
        """Select the fields to be returned."""
        kwargs = {f"{params.fields_mode.value}s": params.fields}
        return s.source(**kwargs)

    @staticmethod
    def process_aggregations(s: Search, aggs: Dict[str, AggregationSetup]) -> Search:
        logger.info("[Process::aggregations] %s", aggs)
        # s.aggs.bucket('total_docs', A('value_count', field='_id'))
        # s.aggs.bucket('total_docs', A('value_count', field='_id'))
        #
        # s.aggs.bucket('per_tag', A('terms', field='event_name'))
        #
        # (s.aggs.bucket('per_tag_2', A('terms', field='event_name'))
        #  .metric('max_lines', 'max', field='lines'))
        #
        # s.aggs.bucket('features', 'nested', path='event_name') \
        #     .metric('name', A('terms', field='event_name'))
        #
        # s.aggs.bucket("aggs", "composite", sources=[
        #     {"event_name": A("terms", field="event_name")},
        #     {"action": A("terms", field="action")}
        # ], size=2)
        #
        # s.aggs.bucket("events_over_time", A(
        #     "date_histogram", field="timestamp", interval="day", format="yyyy-MM-dd"
        # ))
        #
        # s.aggs.bucket("top_actors", A("terms", field="actor.identifier", size=10))
        #
        # s.aggs.bucket("status_distribution", A("terms", field="status", size=10))
        #
        # s.aggs.bucket("context_breakdown", A("terms", field="event_name"))
        #
        # filter_agg = A(
        #     "filter", Q(
        #         "range", timestamp={"gte": "2024-01-01", "lte": "2024-02-01"}
        #     )
        # )
        # terms_agg = A("terms", field="event_name")
        # filter_agg.aggs["context_breakdown"] = terms_agg
        # s.aggs["filtered_context"] = filter_agg

        for agg_name, values in aggs.items():
            field = values.get("field")
            agg_type = values.get("type")

            if agg_type in (AggregationTypeEnum.TERMS, AggregationTypeEnum.VALUE_COUNT):
                # Simple bucket aggregation for type `terms` and `value_count`.
                s.aggs.bucket(agg_name, A(agg_type, field=field))
            if agg_type == AggregationTypeEnum.NESTED:
                # Nested bucket aggregation.
                for value in values.get("sub_aggregations"):
                    path = values.get("path")
                    nested_agg = A(AggregationTypeEnum.NESTED, path=path)
                    terms_agg = A(
                        value.get("type"),
                        field=value.get("field"),
                        size=value.get("max_result"),
                    )
                    if "aggs" not in nested_agg:
                        nested_agg.aggs = {}
                    nested_agg.aggs[terms_agg.name] = terms_agg

                    s.aggs[nested_agg.name] = nested_agg
        return s

    def process_filters(self, s: Search, filters: List[SearchFilterParams]) -> Search:
        for f in filters:
            if f.type == FilterTypeEnum.RANGE:
                s = self.process_filter_type_range(s, f)
            elif f.type == FilterTypeEnum.EXACT:
                self.process_filter_type_exact(s, f)
            elif f.type == FilterTypeEnum.NESTED and ("." in f.field.value):
                self.process_filter_type_nested(s, f)
            elif f.type == FilterTypeEnum.TEXT_SEARCH:
                s = self.process_filter_type_text_search(s, f)
            elif f.type == FilterTypeEnum.WILDCARD:
                s = self.process_filter_type_wildcard(s, f)
            elif f.type == FilterTypeEnum.EXISTS:
                s = self.process_filter_type_exists(s, f)
        return s

    @staticmethod
    def process_filter_type_exact(s: Search, f: SearchFilterParams) -> Search:
        field = (
            "timestamp" if f.field == FieldIdentifierEnum.TIMESTAMP else f.field.value
        )
        return s.query("term", **{field: f.value})

    @staticmethod
    def process_filter_type_nested(s: Search, f: SearchFilterParams) -> Search:
        parent = f.field.value.split(".")[0]
        field = f.field.value.split(".")[1]
        return s.query(
            "nested", path=parent, query=Q("match", **{f"{parent}__{field}": f.value})
        )

    @staticmethod
    def process_filter_type_range(s: Search, f: SearchFilterParams) -> Search:
        field = (
            "timestamp" if f.field == FieldIdentifierEnum.TIMESTAMP else f.field.value
        )
        return s.query("range", **{field: {"gte": f.gte, "lte": f.lte}})

    @staticmethod
    def process_filter_type_text_search(s: Search, f: SearchFilterParams) -> Search:
        return s.query("multi_match", query=f.values[0], fields=[f.field.value])

    @staticmethod
    def process_filter_type_wildcard(s: Search, f: SearchFilterParams) -> Search:
        return s.query("wildcard", **{f.field.value: f.value})

    @staticmethod
    def process_filter_type_exists(s: Search, f: SearchFilterParams) -> Search:
        return s.query("exists", field=f.field.value)
