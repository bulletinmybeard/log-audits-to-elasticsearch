#!/bin/bash

# Generate a random encryption key and export the key
# as an environment variable or modify the kibana.yml file
ENCRYPTION_KEY=$(openssl rand -base64 32)
export XPACK_ENCRYPTEDSAVEDOBJECTS_ENCRYPTIONKEY="${ENCRYPTION_KEY}"

# Execute the original entrypoint of the Kibana Docker image
exec /usr/local/bin/kibana-docker
