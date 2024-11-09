# Start with a lightweight Python base image
FROM python:3.12-slim

# Set environment variables
ENV POETRY_VIRTUALENVS_CREATE=false
ENV PYTHONUNBUFFERED=1
ENV STREAMLIT_SERVER_ADDRESS=0.0.0.0

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Poetry
RUN pip install --no-cache-dir poetry

# Copy shared dependencies, SDK, and frontend files
COPY shared /app/shared
COPY frontend /app/frontend
COPY frontend/sdk /app/frontend/sdk

# Set working directory to the frontend
WORKDIR /app/frontend

# Install project dependencies using Poetry
RUN poetry install --only main

# Expose the port
EXPOSE ${PORT}

# Set the entrypoint for Streamlit
ENTRYPOINT ["poetry", "run", "streamlit", "run"]

# Run the main app file
CMD ["app.py"]