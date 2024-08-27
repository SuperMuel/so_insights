# SO Insights Ingester

## Introduction

The SO Insights Ingester is a crucial component of the SO Insights project, designed to collect, process, and store articles from various online sources. It performs web searches based on predefined queries and stores them in both MongoDB and Pinecone vector database for efficient retrieval and analysis.

## Features

- Asynchronous web searching using DuckDuckGo
- Storage in MongoDB for structured data
- Indexing in Pinecone for vector search capabilities
- Command-line interface

## Prerequisites

- Python 3.12 or higher
- MongoDB
- Pinecone account
- VoyageAI API access

## Installation

Install dependencies using Poetry:
```
poetry install
```

## Configuration

1. Create a `.env` file in the ingester directory with the following contents:

   ```
   MONGODB_URI=your_mongodb_uri
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   VOYAGEAI_API_KEY=your_voyageai_api_key
   ```

2. Adjust the settings in `src/ingester_settings.py` as needed.

## Usage

The Ingester provides several command-line interfaces:

1. Run ingestion for a single search query set:
   ```
   poetry run python main.py run-one <search_query_set_id> [--time-limit <d|w|m|y>]
   ```

2. Run ingestion for all search query sets:
   ```
   poetry run python main.py run-all [--time-limit <d|w|m|y>]
   ```

3. Upsert articles for a specific workspace:
   ```
   poetry run python main.py upsert <workspace_id> [--force]
   ```

4. Upsert articles for all workspaces:
   ```
   poetry run python main.py upsert-all
   ```

## Architecture

The Ingester follows a modular architecture:

- `main.py`: Entry point and CLI commands
- `src/ingester_settings.py`: Configuration management
- `src/search.py`: Web search functionality
- `src/util.py`: Utility functions
- `../shared/`: Shared models and utilities

## Testing

To run tests:

```
poetry run pytest
```
