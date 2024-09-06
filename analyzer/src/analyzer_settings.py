from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class AnalyzerSettings(BaseSettings):
    model_config = SettingsConfigDict(
        case_sensitive=False,
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    MONGODB_URI: str = Field(default=...)

    PINECONE_API_KEY: str = Field(default=...)
    PINECONE_INDEX: str = Field(default=...)

    # minimum number of articles required to start clustering
    MIN_ARTICLES_FOR_CLUSTERING: int = 10

    DEFAULT_MIN_CLUSTER_SIZE: int = 3
    DEFAULT_MIN_SAMPLES: int = 1

    OVERVIEW_GENERATION_MAX_ARTICLES: int = 30
    OVERVIEW_GENERATION_MAX_CONCURRENCY: int = 5

    # when the number of clusters found is less than this value
    # we will also include the clusters summaries (instead of just the titles)
    # as material for the summary of session
    INCLUDE_CLUSTER_SUMMARIES_FOR_SESSION_SUMMARY_THRESHOLD: int = Field(default=10)

    SESSION_SUMMARY_MAX_CLUSTERS: int = 400

    # Watcher settings
    POLLING_INTERVAL_S: int = 10
    MAX_RUNTIME_S: int = 30 * 60  # 30 minutes
    PORT: int = 8080
