FROM python:3.12-slim
WORKDIR /app


ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    POETRY_VERSION=1.8.4 \
    POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1

# PostgreSQL 의존성 설치
RUN apt-get update \
    && apt-get install -y libpq-dev gcc \
    && rm -rf /var/lib/apt/lists/*

# Poetry 설치
RUN pip install "poetry==$POETRY_VERSION"
ENV PATH="$POETRY_HOME/bin:$PATH"

# 의존성 파일 복사 및 설치
COPY pyproject.toml poetry.lock ./
RUN poetry install --no-root --no-dev


CMD ["sh", "-c", "poetry lock --no-update && poetry install && poetry run python manage.py makemigrations && poetry run python manage.py migrate && poetry run uvicorn config.asgi:application --host 0.0.0.0 --port 8000"]
