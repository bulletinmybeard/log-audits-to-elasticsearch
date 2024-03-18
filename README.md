# service-audit

Python REST API service for audit logging

```bash
# Create a new Docker network for the services
docker network create --driver bridge --subnet=172.70.0.0/16 --gateway=172.70.0.1 service_audit
```

```bash
# Create a new index for audit logs
curl -X PUT "http://elasticsearch:9200/audit_log" -H 'Content-Type: application/json' -d'{ "settings": { "number_of_shards": 1, "number_of_replicas": 0 } }'

# Create a new index for audit logs with a mapping
curl -X PUT "http://elasticsearch:9200/audit_log" -H 'Content-Type: application/json' -d'
{
  "settings": {
    "number_of_shards": 1,
    "number_of_replicas": 0
  },
  "mappings": {
    "properties": {
      "game_id": { "type": "keyword" },
      "platform": { "type": "keyword" },
      "version": { "type": "keyword" },
      "service": { "type": "keyword" },
      "object_type": { "type": "keyword" },
      "object_key": { "type": "keyword" },
      "object_name": { "type": "keyword" },
      "object_data": { "type": "text" },
      "extra_fields": { "type": "object" },
      "action": { "type": "keyword" },
      "user": { "type": "keyword" },
      "comment": { "type": "text" },
      "timestamp": { "type": "date" }
    }
  }
}'

# Create an index lifecycle policy to never delete any audit log documents
curl -X PUT "http://elasticsearch:9200/_ilm/policy/never_delete" -H 'Content-Type: application/json' -d '
{
  "policy": {
    "phases": {
      "hot": {
        "min_age": "0ms",
        "actions": {
          "rollover": {
            "max_age": "36500d"
          }
        }
      },
      "delete": {
        "min_age": "36500d",
        "actions": {}
      }
    }
  }
}'

# Apply the index lifecycle policy to the audit_log index
curl -X PUT "http://elasticsearch:9200/audit_log/_settings" -H 'Content-Type: application/json' -d '
{
  "index": {
    "lifecycle": {
      "name": "never_delete",
      "rollover_alias": "audit_log"
    }
  }
}'
```

```bash
# Index mapping for audit logs
{
  "mappings": {
    "properties": {
      "id": {
        "type": "keyword"
      },
      "user": {
        "type": "keyword"
      },
      "action": {
        "type": "keyword"
      },
      "entity": {
        "type": "keyword"
      },
      "entityId": {
        "type": "keyword"
      },
      "timestamp": {
        "type": "date"
      },
      "details": {
        "type": "object",
        "properties": {
          "documentName": {
            "type": "keyword"
          },
          "operation": {
            "type": "keyword"
          }
          // Add extra fields here as needed
        }
      }
    }
  }
}
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

## Search Endpoint Filters (WIP)

The search endpoint supports the following `POST` param filters:

| Parameter   | Example              | Default    | Info                    |
|:------------|:---------------------|:-----------|:------------------------|
| max_results | 10 (int)             | 50         | fewfwe                  |
| fields      | ["service", "action"] | all fields | Elastic document fields |

```json
{
  "max_results": 2,
  "fields": ["service", "action"],
  ...
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
- [ ] Finalize Pydantic models for request and response data
- [ ] Add API tests
- [ ] Add API middlewares
- [ ] Add CI/CD pipeline / Workflows / Actions
