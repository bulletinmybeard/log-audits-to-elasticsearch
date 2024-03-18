# service-audit

Python REST API service for audit logging, which is currently under development.

> **WORK IN PROGRESS!!!!!**

```bash
# Create a new Docker network for the services
docker network create --driver bridge --subnet=172.70.0.0/16 --gateway=172.70.0.1 service_audit
```

## Pre-Commit Hook

Install the hook to run the linter before each commit
```bash
pre-commit install
```

Run the hook manually
```bash
pre-commit run --all-files
```

Auto run the hook before each commit
```bash
pre-commit autoupdate
```

Skipping the hook
```bash
git commit --no-verify -m "Your commit message"
```

Uninstall the hook
```bash
pre-commit uninstall
```

## Search Endpoint Filters
The search endpoint supports various `POST` parameters for filtering search results and enabling customizable queries. Below is a detailed overview of each supported parameter.

### Limit
The `max_results` parameter controls the maximum number of search hits to return. It provides a way to paginate results or limit the response size for large datasets.

| Parameter     | Type    | Range | Default |
|---------------|---------|-------|---------|
| `max_results` | Integer | 1–500 | 500     |


#### Example Usage:
limit the search results to `10` items:

```json
{
  "max_results": 10
}
```

### Fields
The `fields` parameter specifies which document fields to include in the search results. By default, all fields are included.

| Parameter | Type                | Default  |
|-----------|---------------------|----------|
| `fields`  | List[str] or string | "all"     |

#### Example Usage:
Retrieve only the fields `event_name` and `timestamp`:

```json
{
  "fields": ["event_name", "timestamp"]
}
```

### Sort By and Sort Order
Use the `sort_by` and `sort_order` parameters determine the field by which search results are sorted and the direction of the sort, respectively.

| Parameter   | Type   | Default     |
|-------------|--------|-------------|
| `sort_by`   | string | "timestamp" |
| `sort_order`| string | "asc"       |

#### Example Usage:
Sort search results by `event_name` in descending order:

```json
{
"sort_by": "event_name",
"sort_order": "desc"
}
```

### Date Range
The `date_range_start` and `date_range_end` parameters filter search results to only include hits within the specified date range.

| Parameter        | Type   | Default   |
|------------------|--------|-----------|
| `date_range_start` | string | None    |
| `date_range_end`   | string | None    |

#### Example Usage:
Filter search results between January 1st and January 31st, 2024:

```json
{
  "date_range_start": "2024-01-01T00:00:00Z",
  "date_range_end": "2024-01-31T23:59:59Z"
}
```

### Search Query (WIP)
The `search_query` parameter enables a free-text search within the indexed documents.

| Parameter     | Type   | Default |
|---------------|--------|---------|
| `search_query`| string | None    |

#### Example Usage:
Search for documents related to "last update":

```json
{
  "search_query": "last update"
}
```

### Exact Matches
The `exact_matches` parameter allows filtering search results based on exact matches for specified fields.

| Parameter      | Type                      | Default      |
|----------------|---------------------------|--------------|
| `exact_matches`| Dict[str, Union[str, List[str]]] | None  |

#### Example Usage:
Find documents where `status` is "success" and `action` is "login":

```json
{
  "exact_matches": {
    "status": "success",
    "action": "login"
  }
}
```

### Combined Parameters
The following examples demonstrate how to combine various search parameters to achieve precise, customized search results that cater to different query needs and scenarios.

#### Example 1: Date Range with Exact Matches and Sorting
```json
{
  "date_range_start": "2024-01-01T00:00:00Z",
  "date_range_end": "2024-01-31T23:59:59Z",
  "exact_matches": {
    "event_name": "data_backup"
  },
  "sort_by": "timestamp",
  "sort_order": "desc"
}
```

#### Example 2: Free Text Search with Field Limitation and Ascending Sort Order
```json
{
  "search_query": "login success",
  "fields": ["event_name", "timestamp"],
  "sort_by": "event_name",
  "sort_order": "asc"
}
```

#### Example 3: Exclusions with Date Range and Aggregations
```json
{
  "date_range_start": "2024-02-01T00:00:00Z",
  "date_range_end": "2024-02-28T23:59:59Z",
  "exclusions": {
    "event_name": ["role_update", "file_access"]
  },
  "aggregations": {
    "status_counts": {
      "terms": {
        "field": "status"
      }
    }
  }
}
```

#### Example 4: Combining Free Text and Exact Matches with Minimum Should Match
```json
{
  "search_query": "critical update",
  "exact_matches": {
    "context": "system_maintenance"
  },
  "min_should_match": 1,
  "sort_by": "timestamp",
  "sort_order": "desc"
}
```

### Example 5: Nested Field Inclusion with Date Range and Custom Fields
```json
{
  "date_range_start": "2024-03-01T00:00:00Z",
  "date_range_end": "2024-03-15T23:59:59Z",
  "fields": ["timestamp", "actor.identifier", "actor.user_agent", "resource.type"],
  "include_nested": true
}
```


## Code Quality and Testing
These commands are essential to ensuring that the codebase remains clean, well-organized, and thoroughly tested.

### Code Formatting and Linting

Formats all Python files in the project directory to adhere to the Black code style.
```bash
poetry run black .
```

Sorts the imports in all Python files in the project directory alphabetically, and automatically separated into sections.
```bash
poetry run isort .
```

Checks the project directory for any linting errors, including compliance with PEP 8.
```bash
poetry run flake8 .
```

Runs Flake8 linting, excluding any files in the `venv` directory.
```bash
poetry run flake8 --exclude=venv
```

Performs static type checking on all Python files in the project directory.
```bash
poetry run mypy .
```

Runs MyPy for static type checking, excluding files in the `venv` directory.
```bash
poetry run mypy . --exclude venv
```

### Running Tests (WIP)
Runs all tests with Pytest under coverage, displaying print statements (`-s`).
```bash
poetry run coverage run -m pytest -s
```

Runs all tests with verbose output (`-vv` for very verbose) and displaying all print statements.
```bash
poetry run coverage run -m pytest -s -vv
```

## TODO
- [ ] Finalize the README and documentation
- [ ] Finalize the audit log search filters (`/search`)
- [x] Finalize Pydantic models for request and response data
- [ ] Finalize Elasticsearch and Kibana authentication
- [x] Update the document log entry mappings
- [ ] Add API tests
- [ ] Add API middlewares
- [ ] Add CI/CD pipeline / Workflows / Actions
