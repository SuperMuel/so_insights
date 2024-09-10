# SO Insights Ingester

## Introduction

The SO Insights Ingester is a crucial component of the SO Insights project, designed to collect, process, and store articles from various online sources. It performs web searches based on predefined queries and stores them in both MongoDB and Pinecone vector database for efficient retrieval and analysis.

## Features

- Asynchronous web searching using DuckDuckGo
- Storage in MongoDB for structured data
- Indexing in Pinecone for vector search capabilities
- Command-line interface
- Watching for tasks and executing them

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

1. Run ingestion for a single config:
   ```
   poetry run python main.py create-ingestion-task <config_id> 
   ```

2. Run ingestion for all search configs:
   ```
   poetry run python main.py create-ingestion-tasks 
   ```

3. Upsert articles for a specific workspace:
   ```
   poetry run python main.py upsert <workspace_id> [--force]
   ```

4. Upsert articles for all workspaces:
   ```
   poetry run python main.py upsert-all
   ```

5. Watch for tasks and execute them in the background:
   ```
   poetry run python main.py watch
   ```