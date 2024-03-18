#!/bin/bash

# Run the health check script
/usr/share/elasticsearch/config/scripts/check_elasticsearch_health.sh

# Then execute the default Elasticsearch entrypoint
exec /usr/local/bin/docker-entrypoint.sh "$@"
