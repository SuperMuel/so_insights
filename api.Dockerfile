FROM python:3.12-slim

ENV POETRY_VIRTUALENVS_CREATE false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy the project files
COPY shared /app/shared
COPY backend /app/backend

WORKDIR /app/backend

# Install project dependencies
RUN poetry install --only main

EXPOSE ${PORT}

# Command to run the application
CMD poetry run uvicorn src.api:app --host 0.0.0.0 --port ${PORT:-8000}