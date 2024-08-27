# SO Insights Analyzer

## Introduction

The SO Insights Analyzer is a powerful component of the SO Insights project, designed to process large volumes of articles, identify topics through clustering, and evaluate them and generate human-readable insights using LLMs. It works in tandem with the Ingester component to provide high-level analysis of collected data.

## Features

- Clustering using HDBSCAN algorithm
- Generation of titles and summaries for clusters using LLMs
- Evaluation of clusters based on user preferences using LLMs
- Asynchronous design
- Command line interface

## Prerequisites

- Python 3.12 or higher
- MongoDB
- Pinecone Index
- OpenAI API Key

## Installation
Install dependencies using Poetry:
```
poetry install
```

## Configuration

1. Create a `.env` file in the analyzer directory with the following contents:

   ```
   MONGODB_URI=your_mongodb_uri
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   OPENAI_API_KEY=your_openai_api_key
   ```

2. Adjust the settings in `src/analyzer_settings.py` as needed.

## Usage

The Analyzer provides several command-line interfaces:

1. Analyze a specific workspace:
   ```
   poetry run analyzer analyze <workspace_id> [--days <number_of_days>]
   ```

2. Analyze all workspaces:
   ```
   poetry run analyzer analyze-all [--days <number_of_days>]
   ```

3. Generate overviews for specific clustering sessions:
   ```
   poetry run analyzer generate-overviews <session_id1> <session_id2> ... [--only-missing]
   ```

4. Evaluate clusters:
   ```
   poetry run analyzer evaluate <session_id1> <session_id2> ...
   ```

5. Repair missing overviews and evaluations:
   ```
   poetry run analyzer repair
   ```

## Architecture

The Analyzer follows a modular architecture:

- `main.py`: Entry point and CLI commands
- `src/analyzer.py`: Core analysis logic
- `src/clustering_engine.py`: HDBSCAN-based clustering
- `src/cluster_overview_generator.py`: Cluster summary generation
- `src/evaluator.py`: Cluster evaluation
- `src/vector_repository.py`: Pinecone interface to retrieve vectors

## Testing

To run tests:

```
poetry run pytest
```
