# Choose a python image for linux/arch64
FROM python:3.11.6

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=on \
    PIP_DEFAULT_TIMEOUT=100 \
    POETRY_VERSION=1.6.1 \
    POETRY_NO_INTERACTION=1 \
    POETRY_CACHE_DIR=/opt/.cache/poetry_cache


WORKDIR /usr/src/app

RUN pip install "poetry==$POETRY_VERSION"
RUN poetry config virtualenvs.create false

COPY poetry.lock .
COPY pyproject.toml .
COPY README.md .

RUN poetry install --no-ansi --no-root

COPY . .

EXPOSE 8501

RUN poetry install --no-ansi
