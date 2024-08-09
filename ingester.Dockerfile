# Use a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV POETRY_VIRTUALENVS_CREATE=false

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy shared dependencies and ingester project files
COPY shared /app/shared
COPY ingester /app/ingester

WORKDIR /app/ingester

# Install project dependencies
RUN poetry install --only main

# Command to run the ingester application
CMD ["poetry", "run", "python", "main.py"]
