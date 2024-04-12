#!/bin/bash

# Elasticsearch URL
ELASTICSEARCH_URL="http://localhost:9200"

# Wait for Elasticsearch to start and be in a 'yellow' or 'green' state
#curl --silent --fail "http://localhost:9200/_cluster/health?wait_for_status=yellow&timeout=50s"
until $(curl --output /dev/null --silent --fail "$ELASTICSEARCH_URL/_cluster/health?wait_for_status=yellow&timeout=50s"); do
    printf '.'
    sleep 5
done

echo "Elasticsearch is up and running."
