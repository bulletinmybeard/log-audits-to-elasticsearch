ARG KIBANA_VERSION="7.17.10"
FROM arm64v8/kibana:${KIBANA_VERSION}

USER root

ENV \
    ELASTICSEARCH_USERNAME=${ELASTIC_USERNAME} \
    ELASTICSEARCH_PASSWORD=${ELASTIC_PASSWORD}

RUN mkdir -p /opt/shell-scripts

COPY ./*.sh /opt/shell-scripts

RUN chmod +x /opt/shell-scripts/*.sh

CMD find /opt/shell-scripts/ -name "*.sh" -print0 | xargs -0 -I {} bash {}

USER kibana
