# Shared

## Overview

Providing common functionality, data models, and utilities used across multiple parts of the system, including the Ingester, Analyzer, and Backend components.

This module serves as a central repository for shared code, ensuring consistency and reducing duplication across the project.

## Usage

The Shared module is used by:

- `./ingester`: For data collection and storage
- `./analyzer`: For data processing and insights generation
- `./backend`: For API endpoints and data management

## Key Components

### Data Models

1. **Workspace**: Think of this as a project folder. It's where all the settings and information for a specific topic or research area are kept.

2. **IngestionConfig**: This is like a recipe for collecting information. It tells the system where to look for articles and how to gather them.

3. **SearchIngestionConfig**: A specific type of recipe that focuses on web searches to find articles. (Currently DuckDuckGo news)

4. **RssIngestionConfig**: Another recipe type, but this one is for collecting articles from RSS feeds (like news feeds).

5. **IngestionRun**: This represents one round of information gathering. It keeps track of when the gathering started, finished, and how it went.

6. **Article**: This is a single piece of content, like a news article or blog post, that the system has collected.

7. **ClusteringSession**: Represents a complete execution of the clustering algorithm on a set of articles. It includes metadata such as the time range of articles processed, the number of clusters formed, and various statistics about the clustering results.

8. **Cluster**: Represents a group of thematically related articles identified by the clustering algorithm. Each cluster contains references to its member articles, typically sorted by their relevance or similarity to the cluster's central theme. Clusters are the primary output of the analysis process, providing a structured way to navigate and understand large volumes of content.

9. **ClusterOverview**: LLM-generated title and summary of a cluster's content that captures the main theme or topic shared by the majority of articles in the cluster. This overview is essential for quickly understanding the content of a cluster without needing to read all its articles.

10. **ClusterEvaluation**: LLM-generated assessment of a cluster's quality and relevance to the workspace's focus. This evaluation helps prioritize clusters for user review and can be used to refine the clustering process.

11. **ClusterFeedback**: This allows users to say whether they found a particular group of articles useful or not helps improve the analysis process over time.

12. **Starters**: These are pre-made questions or conversation starters to help users begin exploring the collected information using the chatbot

### Utilities

The module also includes various utility functions and classes to help with common tasks across the project, such as:

- Database operations
- Language and region handling
- Validation
- Unique article set management

## Testing

The Shared module includes its own set of tests to ensure the reliability of its components. To run the tests, use the following command from the `shared` directory:

```
poetry run pytest
```