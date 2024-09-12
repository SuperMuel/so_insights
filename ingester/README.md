# SO Insights Ingester

## Introduction

The SO Insights Ingester is a crucial component of the SO Insights project, designed to collect, process, and store articles from various online sources. It performs web searches and RSS feed ingestion based on predefined queries and configurations, storing the results in both MongoDB and Pinecone vector database for efficient retrieval and analysis.

## Features

- Asynchronous web searching using DuckDuckGo
- RSS feed ingestion
- Storage in MongoDB for structured data
- Indexing in Pinecone for vector search capabilities
- Command-line interface for various operations
- Task watching and execution system

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

1. Create an ingestion task for a single config:
   ```
   poetry run python main.py create-ingestion-task <config_id>
   ```

2. Create ingestion tasks for all configs:
   ```
   poetry run python main.py create-ingestion-tasks [--workspace-id <workspace_id>] [--type <ingestion_type>]
   ```

3. Sync vector database:
   ```
   poetry run python main.py sync-vector-db [--workspace-id <workspace_id>] [--force]
   ```

4. Watch for tasks and execute them:
   ```
   poetry run python main.py watch [--interval <seconds>] [--max-runtime <seconds>]
   ```

## Project Structure

```
ingester
├── main.py               # Main entry point and CLI commands
├── pyproject.toml        # Project configuration and dependencies
├── README.md             # Project documentation
├── src
│   ├── ingester_settings.py     # Configuration settings
│   ├── mongo_db_operations.py   # MongoDB operations
│   ├── rss.py                   # RSS feed ingestion
│   ├── search.py                # Web search functionality
│   ├── vector_indexing.py       # Vector database operations
│   └── __init__.py
└── tests
    ├── test_rss.py              # Tests for RSS functionality
    └── __init__.py
```

## Core Functionalities

- Task Creation: Ingestion tasks are created based on configurations.
- Web Search: Performs searches using DuckDuckGo API based on predefined queries.
- RSS Feed Ingestion: Fetches and processes articles from RSS feeds.
- Data Storage: Stores articles in MongoDB and indexes them in Pinecone.
- Vector Synchronization: Ensures MongoDB and Pinecone are in sync.

## Testing

Run tests using pytest:

```
poetry run pytest
```