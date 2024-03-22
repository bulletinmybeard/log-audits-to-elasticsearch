ARG PYTHON_VERSION="3.12.2"

FROM python:${PYTHON_VERSION}-alpine

# Docker build arguments
ARG POETRY_VERSION="1.8.2"
ARG ENVIRONMENT="development"
ARG X_API_KEY=""
ARG ENABLE_HEALTHCHECK="false"
ARG LOG_LEVEL="info"

ARG ELASTIC_INDEX_NAME="audit_log"
ARG ELASTIC_POLICY_NAME="never_delete"
ARG ELASTICSEARCH_HOST="http://elasticsearch:9200"
ARG KIBANA_HOST="http://kibana:5601"
ARG ELASTIC_USERNAME=""
ARG ELASTIC_PASSWORD=""

# Environment variables
ENV \
    ENVIRONMENT=${ENVIRONMENT} \
    X_API_KEY=${X_API_KEY} \
    POETRY_VERSION=${POETRY_VERSION} \
    API_DIR=/app \
    API_PORT=${API_PORT} \
    LOG_LEVEL=${LOG_LEVEL} \
    ENABLE_HEALTHCHECK=${ENABLE_HEALTHCHECK} \
    ELASTIC_INDEX_NAME=${ELASTIC_INDEX_NAME} \
    ELASTIC_POLICY_NAME=${ELASTIC_POLICY_NAME} \
    ELASTIC_USERNAME=${ELASTIC_USERNAME} \
    ELASTIC_PASSWORD=${ELASTIC_PASSWORD} \
    ELASTICSEARCH_HOST=${ELASTICSEARCH_HOST} \
    KIBANA_HOST=${KIBANA_HOST}

# Create a non-root user
RUN addgroup -g 1000 auditor && \
    adduser -D -u 1000 -G auditor auditor

# Install system dependencies
RUN \
    apk update && \
    apk add --no-cache \
    bash \
    build-base \
    gcc \
    curl \
    libffi-dev \
    jq

WORKDIR /app

COPY ./docker/service-audit/entrypoint.sh /opt/entrypoint.sh
RUN chmod +x /opt/entrypoint.sh

RUN \
    pip install --upgrade pip && \
    pip install --no-cache-dir poetry==${POETRY_VERSION} && \
    rm -rf /root/.cache/pip/ && \
    poetry config virtualenvs.create false

# Docker healthcheck configuration
HEALTHCHECK \
    --interval=30s \
    --timeout=10s \
    --start-period=1m \
    --retries=3 \
    CMD if [ "$ENABLE_HEALTHCHECK" = "true" ]; then curl --fail http://127.0.0.1:8000/healthcheck || exit 1; else exit 0; fi

COPY pyproject.toml poetry.lock ./
RUN \
    poetry config virtualenvs.create false && \
    poetry install --no-interaction --no-ansi && \
    rm -rf /root/.cache/pypoetry/*

USER auditor

ENTRYPOINT ["/opt/entrypoint.sh"]
