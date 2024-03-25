from typing import Any, Dict, List

from elasticsearch import Elasticsearch
from elasticsearch_dsl import A, Search
from fastapi import HTTPException

from service_audit.custom_logger import get_logger
from service_audit.models import (
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

        s = s.extra(from_=0, size=params.max_results, track_total_hits=True)

        s = self.sort_order(s, params)

        if params.fields:
            s = self.select_fields(s, params)

        if params.filters:
            s = self.process_filters(s, params.filters)

        if params.aggs:
            s = self.process_aggregations(s, params.aggs)

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
    def process_aggregations(s: Search, aggs: Dict[str, AggregationSetup]) -> Search:
        print("[Process::aggregations]", aggs)

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
                s.aggs.bucket(agg_name, A(agg_type, field=field))
            if agg_type == AggregationTypeEnum.NESTED:
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

    @staticmethod
    def process_filters(s: Search, filters: List[SearchFilterParams]):
        """Processes the filters applied to the search query."""
        for f in filters:
            if f.type == FilterTypeEnum.RANGE:
                if f.field == FieldIdentifierEnum.TIMESTAMP:
                    s = s.query("range", timestamp={"gte": f.gte, "lte": f.lte})
                else:
                    kwargs = {f"{f.field}": {"gte": f.gte, "lte": f.lte}}
                    s.query("range", **kwargs)
            elif f.type == FilterTypeEnum.EXACT:
                if f.field == FieldIdentifierEnum.TIMESTAMP:
                    s = s.query("term", timestamp=f.value)
                else:
                    s = s.query("term", **{f.field: f.value})
            elif f.type == FilterTypeEnum.TEXT_SEARCH:
                s = s.query("multi_match", query=f.values[0], fields=[f.field])
            elif f.type == FilterTypeEnum.WILDCARD:
                s = s.query("wildcard", **{f.field: f.value})
            elif f.type == FilterTypeEnum.EXISTS:
                s = s.query("exists", field=f.field)
        return s

    @staticmethod
    def sort_order(s: Search, params: SearchParamsV2):
        """Sorts the search results by a given field and order."""
        return s.sort({params.sort_by: {"order": params.sort_order}})

    @staticmethod
    def select_fields(s: Search, params: SearchParamsV2):
        """Selects the fields to be returned in the search results."""
        kwargs = {f"{params.fields_mode.value}s": params.fields}
        return s.source(**kwargs)
