# SoInsights Ingester

## Project Overview

SoInsights Ingester is a powerful tool designed to collect, process, and store news articles related to Artificial Intelligence from various online sources. It's part of a larger system that aims to provide insights and analysis on AI trends and developments.

## Features

- Automated search and collection of AI-related news articles
- Configurable search queries and regions
- Deduplication of articles to ensure unique content
- Integration with MongoDB for data storage
- Vector indexing of articles for efficient retrieval and analysis
- Configurable ingestion runs with customizable time limits
- Robust error handling and logging

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/your-repo/so-insights-ingester.git
   cd so-insights-ingester
   ```

2. Install dependencies using Poetry:
   ```
   poetry install
   ```

## Configuration

1. Create a `.env` file in the `ingester` directory with the following variables:
   ```
   MONGODB_URI=your_mongodb_connection_string
   VOYAGEAI_API_KEY=your_voyageai_api_key
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   ```

2. If needed, adjust the settings in `src/ingester_settings.py` by setting up more environment variables.

## Usage

The ingester can be run using the following commands:

1. Run ingestion for a single SearchQuerySet:
   ```
   poetry run python main.py run-one <search_query_set_id> --time-limit d
   ```

2. Run ingestion for all SearchQuerySets:
   ```
   poetry run python main.py run-all --time-limit w
   ```

3. Upsert articles for a single workspace:
   ```
   poetry run python main.py upsert <workspace_id>
   ```

4. Upsert articles for all workspaces:
   ```
   poetry run python main.py upsert-all
   ```

## Code Structure

- `main.py`: Entry point of the application
- `src/`:
  - `ingester_settings.py`: Configuration settings
  - `search.py`: Functions for searching and retrieving articles
  - `util.py`: Utility functions

## Key Components

1. **SearchQuerySet**: Defines a set of search queries and parameters for article collection.
2. **IngestionRun**: Represents a single run of the ingestion process, tracking status and results.
3. **Article**: Data model for storing article information.
4. **VectorIndexing**: Indexes articles for efficient similarity search and retrieval.
