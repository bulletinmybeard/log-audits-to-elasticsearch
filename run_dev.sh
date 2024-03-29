#!/bin/bash

# Read environment variables from .env file.
set -a
source .env
set +a

# Check if Poetry is installed.
if ! command -v poetry &> /dev/null; then
    echo "Poetry could not be found. Install Poetry to continue."
    exit 1
fi

# Ensure the Poetry virtual environment is ready and dependencies are up to date.
echo "Checking virtual environment and dependencies..."
poetry install --no-root

# Overwrite `CONFIG_FILE_PATH` environment variable.
export CONFIG_FILE_PATH="config.yaml"

# Run the FastAPI application with Uvicorn.
poetry run uvicorn audit_logger.main:app \
    --host "0.0.0.0" \
    --log-level "info" \
    --reload
