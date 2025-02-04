# SO Insights Analyzer

## Introduction

The SO Insights Analyzer is a powerful component of the SO Insights project, designed to process large volumes of articles, identify topics through clustering, and generate human-readable insights using LLMs. It works in tandem with the Ingester component to provide high-level analysis of collected data.

## Key Concepts

Before diving into the features, let's explain some key concepts:

- **Embedding**: A numerical representation of text that captures its semantic meaning. Embeddings allow us to compare and analyze text data mathematically.
- **Vector**: In this context, a vector is the mathematical representation of an embedding. Each article is represented as a vector in a high-dimensional space.
- **Clustering**: The process of grouping similar articles together based on their vector representations.
- **HDBSCAN**: Hierarchical Density-Based Spatial Clustering of Applications with Noise, the algorithm we use for clustering.

## Features

- **Clustering using HDBSCAN algorithm**: Groups similar articles together, helping identify main themes and topics across large sets of articles.
- **Generation of titles and summaries for clusters using LLMs**: Provides human-readable overviews of each cluster's content.
- **Evaluation of clusters based on user preferences using LLMs**: Assesses the relevance and quality of identified topics to the workspace's focus.
- **Generation of conversation starters**: Creates engaging questions based on the analyzed data to facilitate user interaction with the chatbot.
- **Task watching and execution**: Automatically processes new clustering tasks as they arrive.

## Key Components

1. **Analyzer** (analyzer.py): The core class that orchestrates the entire analysis process.
2. **ClusteringEngine** (clustering_engine.py): Performs the HDBSCAN clustering on article embeddings.
3. **ClusterOverviewGenerator** (cluster_overview_generator.py): Generates summaries for each cluster using LLMs.
4. **ClusterEvaluator** (evaluator.py): Assesses the relevance of clusters to the workspace's focus.
5. **SessionSummarizer** (session_summary_generator.py): Creates an overall summary of a clustering session.
6. **ConversationStartersGenerator** (starters_generator.py): Generates engaging questions based on the analyzed data.
7. **VectorRepository** (vector_repository.py): Interfaces with Pinecone to retrieve article embeddings.

## Benefits

- **Topic Discovery**: Automatically identifies main themes and topics in large sets of articles.
- **Content Summarization**: Provides concise overviews of clustered content, saving time in information processing.
- **Relevance Assessment**: Evaluates the importance of discovered topics to the user's interests.
- **User Engagement**: Generates conversation starters to encourage interaction with the analyzed data using the chatbot.
- **Flexibility**: Adapts to different languages and topics as defined by each workspace.

## Prerequisites

- Python 3.12 or higher
- MongoDB populated with articles found by the Ingester
- Pinecone Vector Database with embeddings of the articles from the Ingester
- OpenAI API Key for LLM-based tasks

Optional:
- Langsmith project and API key for monitoring LLM performance

## Installation

Install dependencies using Poetry:
```
poetry install
```

## Configuration

1. Create a `.env` file in the analyzer directory with the following contents:

   ```
   MONGODB_URI=your_mongodb_uri
   MONGODB_DATABASE=your_mongodb_database_name
   PINECONE_API_KEY=your_pinecone_api_key
   PINECONE_INDEX=your_pinecone_index_name
   OPENAI_API_KEY=your_openai_api_key
   ```

2. Adjust the settings in `src/analyzer_settings.py` as needed.

## Usage

The Analyzer provides several command-line interfaces:

```bash
# Create analysis tasks
poetry run analyzer create-analysis-tasks [WORKSPACE_IDS] [--days DAYS]

# Generate overviews
poetry run analyzer generate-overviews SESSION_IDS [--only-missing]

# Evaluate clusters
poetry run analyzer evaluate SESSION_IDS

# Generate conversation starters
poetry run analyzer generate-starters

# Summarize a session
poetry run analyzer summarize-session SESSION_ID

# Repair missing data
poetry run analyzer repair

# Watch for and process tasks
poetry run analyzer watch [--interval SECONDS] [--max-runtime SECONDS]
```


## Key Models

The analyzer works with several important data models:

- **Workspace**: Represents a project or topic, containing settings and metadata for all related content.
- **Article**: Represents a single piece of content (e.g., news article, blog post) collected during ingestion.
- **AnalysisRun**: Represents a single run of the analysis process on a set of articles. It also maintains the state of the task.
- **Cluster**: A group of related articles identified during clustering.
- **ClusterOverview**: A summary of a cluster's content, including a title and brief description.
- **ClusterEvaluation**: An assessment of a cluster's relevance and quality.
- **Starters**: Predefined conversation starters or prompts for the workspace's chatbot.

## Testing

To run tests:

```
poetry run pytest
```
