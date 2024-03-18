# service-audit

Python REST API service for audit logging, which is currently under development.

> **WORK IN PROGRESS!!!!!**

```bash
# Create a new Docker network for the services
docker network create --driver bridge --subnet=172.70.0.0/16 --gateway=172.70.0.1 service_audit
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
- [ ] Finalize Elasticsearch and Kibana authentication
- [ ] Update the document log entry schema
- [ ] Add API tests
- [ ] Add API middlewares
- [ ] Add CI/CD pipeline / Workflows / Actions
