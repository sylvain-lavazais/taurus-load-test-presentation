FROM python:3.12-slim AS builder

COPY . /build

WORKDIR /build

RUN apt-get update && \
    apt-get install -y gcc iputils-ping wget jq libpq-dev && \
    pip install -U pip && \
    rm -rf /var/lib/apt/lists/*dock

RUN pip install .

FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

RUN groupadd -g 1000 app && \
    useradd --system --create-home --home-dir /app -s /bin/bash -g app -u 1000 app

USER 1000
WORKDIR /app

COPY --chown=app ./config.toml .

LABEL project-name = 'Api-Test'

EXPOSE 8080

ENV PROMETHEUS_MULTIPROC_DIR="/tmp"

ENTRYPOINT [ "api-test" ]

CMD ["0.0.0.0", "8080"]
