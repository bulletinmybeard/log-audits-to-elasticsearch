#!/bin/bash

wait_for_elasticsearch() {
    echo "Checking if Elasticsearch is up"
    until curl --output /dev/null --silent --head --fail "$ELASTICSEARCH_HOST"; do
        printf '.'
        sleep 5
    done
    echo "Elasticsearch is up and running!"
}

create_elasticsearch_index_with_mappings() {
    curl_output=$(curl -X PUT "$ELASTICSEARCH_HOST/${ELASTIC_INDEX_NAME}" \
        -H 'Content-Type: application/json' \
        -d '{
                "settings": {
                    "number_of_shards": 1,
                    "number_of_replicas": 0
                },
                "mappings": {
                    "properties": {
                        "timestamp": { "type": "date" },
                        "event_name": { "type": "keyword" },
                        "actor": {
                            "type": "nested",
                            "properties": {
                                "identifier": { "type": "keyword" },
                                "type": { "type": "keyword" },
                                "ip_address": { "type": "ip" },
                                "user_agent": { "type": "keyword" }
                            }
                        },
                        "action": { "type": "keyword" },
                        "comment": { "type": "text" },
                        "context": { "type": "keyword" },
                        "resource": {
                            "type": "nested",
                            "properties": {
                                "type": { "type": "keyword" },
                                "id": { "type": "keyword" }
                            }
                        },
                        "operation": { "type": "keyword" },
                        "status": { "type": "keyword" },
                        "endpoint": {
                            "type": "text",
                            "fields": {
                                "keyword": { "type": "keyword", "ignore_above": 256 }
                            }
                        },
                        "server_details": {
                            "type": "nested",
                            "properties": {
                                "hostname": { "type": "keyword" },
                                "vm_name": { "type": "keyword" },
                                "ip_address": { "type": "ip" }
                            }
                        },
                        "meta": {
                            "type": "nested",
                            "dynamic": true
                        }
                    }
                }
            }')

    if [[ "$curl_output" =~ "acknowledged" ]]; then
        echo "Elasticsearch index '${ELASTIC_INDEX_NAME}' created"
    elif [[ "$curl_output" =~ "resource_already_exists_exception" ]]; then
        echo "Elasticsearch index '${ELASTIC_INDEX_NAME}' already exists"
    else
        echo "Failed to create Elasticsearch index '${ELASTIC_INDEX_NAME}'"
        exit 1
    fi
}

create_kibana_index_pattern() {
    echo "Waiting for Kibana to be ready"
    until curl --output /dev/null --silent --head --fail "$KIBANA_HOST"; do
        printf '.'
        sleep 5
    done
    echo "Kibana is ready!"

    existing_pattern=$(curl -s "$KIBANA_HOST/api/saved_objects/_find?type=index-pattern&fields=title" | \
        jq -r --arg ELASTIC_INDEX_NAME "${ELASTIC_INDEX_NAME}" '.saved_objects[] | select(.attributes.title | startswith($ELASTIC_INDEX_NAME)).id')

    if [ -n "$existing_pattern" ]; then
        echo "Index pattern starting with '${ELASTIC_INDEX_NAME}' already exists in Kibana"
        return
    else
        echo "Index pattern starting with '${ELASTIC_INDEX_NAME}' does not exist, creating now..."
    fi

    curl_output=$(curl -X POST "$KIBANA_HOST/api/saved_objects/index-pattern" \
        -H 'Content-Type: application/json' \
        -H 'kbn-xsrf: true' \
        -d '{
            "attributes": {
                "title": "'"${ELASTIC_INDEX_NAME}"*'",
                "timeFieldName": "@timestamp"
            }
        }')

    if echo "$curl_output" | jq -e .id >/dev/null; then
        echo "Index pattern '${ELASTIC_INDEX_NAME}*' created in Kibana"
    else
        echo "Failed to create index pattern '${ELASTIC_INDEX_NAME}*' in Kibana"
        exit 1
    fi
}

create_ilm_policy() {
    policy_exists=$(curl -s -X GET "$ELASTICSEARCH_HOST/_ilm/policy/${ELASTIC_POLICY_NAME}")

    if [[ "$policy_exists" == *"resource_not_found_exception"* ]]; then
        echo "Creating index lifecycle policy '${ELASTIC_POLICY_NAME}'"

        curl_output=$(curl -s -X PUT "$ELASTICSEARCH_HOST/_ilm/policy/${ELASTIC_POLICY_NAME}" \
            -H 'Content-Type: application/json' \
            -d '{
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
            }')

        if [[ "$curl_output" =~ "acknowledged" ]]; then
            echo "Index lifecycle policy '${ELASTIC_POLICY_NAME}' created"
        else
            echo "Failed to create index lifecycle policy '${ELASTIC_POLICY_NAME}'"
            exit 1
        fi
    else
        echo "Index lifecycle policy '${ELASTIC_POLICY_NAME}' exists! (skip)"
    fi
}

apply_ilm_policy_to_index() {
    policy_applied=$(curl -s -X GET "$ELASTICSEARCH_HOST/${ELASTIC_INDEX_NAME}/_settings")

    if [[ ! "$policy_applied" =~ ${ELASTIC_POLICY_NAME} ]]; then
        echo "Applying index lifecycle policy '${ELASTIC_POLICY_NAME}' to index '${ELASTIC_INDEX_NAME}'"

        curl_output=$(curl -s -X PUT "$ELASTICSEARCH_HOST/${ELASTIC_INDEX_NAME}/_settings" \
            -H 'Content-Type: application/json' \
            -d '{
                "index": {
                    "lifecycle": {
                        "name": "'"${ELASTIC_POLICY_NAME}"'",
                        "rollover_alias": "'"${ELASTIC_INDEX_NAME}"'"
                    }
                }
            }')

        if [[ "$curl_output" =~ "acknowledged" ]]; then
            echo "Index lifecycle policy '${ELASTIC_POLICY_NAME}' applied to index '${ELASTIC_INDEX_NAME}'"
        else
            echo "Failed to apply index lifecycle policy '${ELASTIC_POLICY_NAME}' to index '${ELASTIC_INDEX_NAME}'"
            exit 1
        fi
    else
        echo "Index lifecycle policy '${ELASTIC_POLICY_NAME}' is already applied to index '${ELASTIC_INDEX_NAME}'"
    fi
}

wait_for_elasticsearch
create_elasticsearch_index_with_mappings
create_kibana_index_pattern
create_ilm_policy
apply_ilm_policy_to_index

poetry run uvicorn service_audit.main:app \
    --host "0.0.0.0" \
    --log-level "$LOG_LEVEL" \
    --reload

#poetry run gunicorn service_audit.main:app \
#  -k uvicorn.workers.UvicornWorker \
#  -w 4 \
#  --bind 0.0.0.0:8000 \
#  --log-level info
#  --reload

exec "$@"
