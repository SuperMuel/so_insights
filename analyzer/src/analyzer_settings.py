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

    DEFAULT_MIN_CLUSTER_SIZE: int = 6
    DEFAULT_MIN_SAMPLES: int = 3

    OVERVIEW_GENERATION_MAX_ARTICLES: int = 30
    OVERVIEW_GENERATION_MAX_CONCURRENCY: int = 5
