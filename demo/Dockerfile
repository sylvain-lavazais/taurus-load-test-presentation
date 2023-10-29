FROM python:3.11.6-slim
RUN groupadd -g 1000 app && \
    useradd --system --create-home --home-dir /app -s /bin/bash -g app -u 1000 app
WORKDIR /app

LABEL project-name = 'Api-Test'

RUN apt-get update && \
    apt-get install -y gcc iputils-ping wget jq libpq-dev && \
    rm -rf /var/lib/apt/lists/*

USER 1000
WORKDIR /app

COPY --chown=app dist/api_test-*.whl .
COPY --chown=app config.toml .

RUN pip install --user api_test-*.whl

USER root
RUN apt-get remove -y --purge gcc && \
    apt autoremove -y && \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /tmp/wheels  && \
    rm -f import_export_management-*.whl

USER 1000

EXPOSE 8080

ENV PROMETHEUS_MULTIPROC_DIR="/tmp"

ENTRYPOINT [ "api-test" ]
CMD ["0.0.0.0", "8080"]
