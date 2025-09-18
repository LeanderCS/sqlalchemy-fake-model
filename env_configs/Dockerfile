FROM python:3.7-slim

WORKDIR /app

RUN apt-get update  \
    && apt-get install -y git \
    && apt-get clean

COPY pyproject.toml /app

RUN python -m pip install .[dev]

COPY scripts /usr/local/bin
RUN find /usr/local/bin -type f -name "*" -exec chmod +x {} \;

COPY .. /app
