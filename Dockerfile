ARG PYTHON_VERSION=3.10
FROM python:${PYTHON_VERSION}-slim AS base
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_DEFAULT_TIMEOUT=60 \
    POETRY_NO_INTERACTION=1 \
    POETRY_VERSION=${POETRY_VERSION}
RUN pip install setuptools --upgrade
WORKDIR /app

FROM base AS builder

ARG POETRY_VERSION=1.1.15
RUN pip install "poetry==$POETRY_VERSION"
COPY pyproject.toml /app
COPY poetry.lock /app
RUN poetry install --no-root --no-dev

FROM builder AS app
ARG PG_USERNAME="postgres" \
    PG_PASSWORD="" \
    PG_HOST="localhost" \
    PG_PORT="5432" \
    PG_DATABASE="fareview" \
    ENVIRONMENT="development"
ENV PG_USERNAME=${PG_USERNAME} \
    PG_PASSWORD=${PG_PASSWORD} \
    PG_HOST=${PG_HOST} \
    PG_PORT=${PG_PORT} \
    PG_DATABASE=${PG_DATABASE} \
    ENVIRONMENT=${ENVIRONMENT}
COPY . .
CMD ["sh", "-c", "poetry run scrapy list | xargs -n 1 poetry run scrapy crawl"]
