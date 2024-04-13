from datetime import timedelta
from typing import Any, Dict, List, Tuple

from elasticsearch import Elasticsearch
from elasticsearch_dsl import A, Q, Search
from fastapi import HTTPException, status

from audit_logger.custom_logger import get_logger
from audit_logger.models import (
    AggregationTypeEnum,
    FieldIdentifierEnum,
    FilterTypeEnum,
    SearchFilterParams,
    SearchParams,
    current_time,
)

logger = get_logger("audit_logger")


class ElasticSearchQueryBuilder:
    elastic_index_name: str
    s: Search

    def __init__(self, using: Elasticsearch, index: str) -> None:
        self.elastic_index_name = index
        self.s = Search(using=using, index=index)

    def process_parameters(self, params: SearchParams) -> Dict[str, Any]:
        # Set the number of documents to be returned.
        self.s = self.s.extra(from_=0, size=params.max_results, track_total_hits=True)

        # Sort the documents based on the `sort_by` (field) and sort_order (asc/desc).
        self.s = self.sort_order(params)

        # Select the fields to be returned.
        if params.fields:
            self.s = self.select_fields(params)

        # Process all given filters.
        if params.filters:
            self.s = self.process_filters(params.filters)

        # Process all given experimental filters.
        if params.filters_exp:
            self.s = self.process_experimental_filters(params.filters_exp)

        # Process all given aggregations.
        if params.aggs:
            self.s = self.process_aggregations(params.aggs)

        # Execute the search query.
        response = self.s.execute()

        if not response.success():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="Search failed."
            )

        return {
            "docs": [hit.to_dict() for hit in response.hits],
            "aggs": [agg.to_dict() for agg in response.aggs],
            "index_size": response.hits.total.value,
        }

    def sort_order(self, params: SearchParams) -> Search:
        """Sort ES documents based on the `sort_by` (field) and sort_order (asc/desc)."""
        return self.s.sort({params.sort_by: {"order": params.sort_order}})

    def select_fields(self, params: SearchParams) -> Search:
        """Select the fields to be returned."""
        return self.s.source(**{f"{params.fields_mode.value}s": params.fields})

    def process_aggregations(self, aggs: Dict[str, Any]) -> Search:
        for agg_name, values in aggs.items():
            field = values.get("field")
            agg_type = values.get("type")
            if agg_type in (AggregationTypeEnum.TERMS, AggregationTypeEnum.VALUE_COUNT):
                # Simple bucket aggregation for type `terms` and `value_count`.
                self.s.aggs.bucket(agg_name, A(agg_type, field=field))
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

                    self.s.aggs[nested_agg.name] = nested_agg
            return self.s

    def process_filters(self, filters: List[SearchFilterParams]) -> Search:
        for f in filters:
            if f.type == FilterTypeEnum.RANGE:
                self.s = self.process_filter_type_range(f)
            elif f.type == FilterTypeEnum.EXACT:
                self.s = self.process_filter_type_exact(f)
            elif f.type == FilterTypeEnum.NESTED and ("." in f.field.value):
                self.s = self.process_filter_type_nested(f)
            elif f.type == FilterTypeEnum.TEXT_SEARCH:
                self.s = self.process_filter_type_text_search(f)
            elif f.type == FilterTypeEnum.WILDCARD:
                self.s = self.process_filter_type_wildcard(f)
            elif f.type == FilterTypeEnum.EXISTS:
                self.s = self.process_filter_type_exists(f)
        return self.s

    def process_filter_type_exact(self, f: SearchFilterParams) -> Search:
        field = (
            "timestamp" if f.field == FieldIdentifierEnum.TIMESTAMP else f.field.value
        )
        return self.s.query("term", **{field: f.value})

    def process_filter_type_nested(self, f: SearchFilterParams) -> Search:
        parent, field = f.field.value.split(".")
        return self.s.query(
            "nested", path=parent, query=Q("match", **{f"{parent}__{field}": f.value})
        )

    def process_filter_type_range(self, f: SearchFilterParams) -> Search:
        field = (
            "timestamp" if f.field == FieldIdentifierEnum.TIMESTAMP else f.field.value
        )
        if f.value:
            gte, lte = self.calculate_date_range(f.value)
            query_range = {"gte": gte, "lte": lte}
        else:
            query_range = {"gte": f.gte, "lte": f.lte}

        return self.s.query("range", **{field: query_range})

    def process_filter_type_text_search(self, f: SearchFilterParams) -> Search:
        fields = f.fields or [f.field.value]
        return self.s.query("multi_match", query=f.value, fields=fields)

    def process_filter_type_wildcard(self, f: SearchFilterParams) -> Search:
        if "." in f.field.value:
            parent, field = f.field.value.split(".")
            self.s = self.s.query(
                "nested",
                path=parent,
                query=Q("wildcard", **{f"{parent}__{field}": f"{f.value}"}),
            )
        else:
            self.s = self.s.query("wildcard", **{f.field.value: f.value})
        return self.s

    def process_filter_type_exists(self, f: SearchFilterParams) -> Search:
        return self.s.query("exists", field=f.field.value)

    def process_experimental_filters(self, filters: List[Any]) -> Search:
        print("[process_experimental_filters] filters:", filters)
        return self.s

    @staticmethod
    def calculate_date_range(value: str) -> Tuple[str, str]:
        """Calculate 'gte' and 'lte' values based on 'value' (e.g., 'today', 'this-week')."""
        now = current_time()
        if value == "today":
            gte = now.strftime("%Y-%m-%dT00:00:00")
            lte = now.strftime("%Y-%m-%dT23:59:59")
        elif value == "yesterday":
            yesterday = now - timedelta(days=1)
            gte = yesterday.strftime("%Y-%m-%dT00:00:00")
            lte = yesterday.strftime("%Y-%m-%dT23:59:59")
        elif value == "this-week":
            week_start = now - timedelta(days=now.weekday())
            week_end = week_start + timedelta(days=6)
            gte = week_start.strftime("%Y-%m-%dT00:00:00")
            lte = week_end.strftime("%Y-%m-%dT23:59:59")
        elif value == "last-month":
            first_day_last_month = now.replace(day=1) - timedelta(days=1)
            first_day_this_month = now.replace(day=1)
            last_day_last_month = first_day_this_month - timedelta(days=1)
            gte = first_day_last_month.replace(day=1).strftime("%Y-%m-%dT00:00:00")
            lte = last_day_last_month.strftime("%Y-%m-%dT23:59:59")
        else:
            raise ValueError("Unsupported value for date range")

        return gte, lte
